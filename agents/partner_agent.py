"""
AI Partner Chat 智能体
集成个性化对话、向量化检索和记忆管理
"""

from typing import Dict, List, Optional, Any, TypedDict
from datetime import datetime
import json

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from pydantic import BaseModel, Field

from utils.llm import CustomLLM
from utils.vector_store import VectorStore
from utils.persona_manager import PersonaManager
from utils.memory_manager import MemoryManager, ConversationTurn


class AgentState(BaseModel):
    """智能体状态定义"""
    user_message: str = Field(description="用户输入的消息")
    ai_response: str = Field(default="", description="AI 生成的回应")

    # 上下文信息
    persona_context: str = Field(default="", description="用户和AI画像上下文")
    relevant_notes: List[Dict] = Field(default_factory=list, description="相关的历史笔记")
    conversation_context: str = Field(default="", description="对话历史上下文")

    # 检索和搜索结果
    search_query: str = Field(default="", description="用于检索的查询")
    retrieval_results: List[Dict] = Field(default_factory=list, description="检索结果")

    # 工具调用相关
    tool_calls: List[Dict] = Field(default_factory=list, description="工具调用记录")
    tool_results: List[Dict] = Field(default_factory=list, description="工具执行结果")

    # 元数据
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    session_id: str = Field(default="", description="会话ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


class AIPartnerAgent:
    """AI Partner 智能体"""

    def __init__(
        self,
        config_dir: str = "./config",
        vector_db_path: str = "./vector_db",
        memory_dir: str = "./memory"
    ):
        """
        初始化 AI Partner 智能体

        Args:
            config_dir: 配置文件目录
            vector_db_path: 向量数据库路径
            memory_dir: 记忆存储目录
        """
        # 初始化组件
        self.llm = CustomLLM()
        self.vector_store = VectorStore(vector_db_path)
        self.persona_manager = PersonaManager(config_dir)
        self.memory_manager = MemoryManager(memory_dir)

        # 创建或恢复会话
        if not self.memory_manager.current_session:
            self.memory_manager.create_session()
        
        # 检查点保存器（用于状态持久化）
        self.checkpointer = MemorySaver()

        # 构建状态图
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """构建智能体状态图"""

        # 定义状态图
        workflow = StateGraph(AgentState)

        # 添加节点
        workflow.add_node("load_context", self._load_context)
        workflow.add_node("analyze_query", self._analyze_query)
        workflow.add_node("search_notes", self._search_notes)
        workflow.add_node("call_tools", self._call_tools)
        workflow.add_node("generate_response", self._generate_response)
        workflow.add_node("update_memory", self._update_memory)

        # 设置入口点
        workflow.set_entry_point("load_context")

        # 添加边
        workflow.add_edge("load_context", "analyze_query")

        # 条件边：根据分析结果决定下一步
        workflow.add_conditional_edges(
            "analyze_query",
            self._decide_next_step,
            {
                "search": "search_notes",
                "tools": "call_tools",
                "respond": "generate_response"
            }
        )

        workflow.add_edge("search_notes", "generate_response")
        workflow.add_edge("call_tools", "generate_response")
        workflow.add_edge("generate_response", "update_memory")
        workflow.add_edge("update_memory", END)

        return workflow.compile(checkpointer=self.checkpointer)

    async def _load_context(self, state: AgentState) -> AgentState:
        """加载画像和对话上下文"""
        print("🔍 加载画像和上下文...")

        # 加载画像上下文
        persona_context = self.persona_manager.get_persona_context()

        # 加载对话上下文
        conversation_context = self.memory_manager.get_current_context(max_turns=3)

        # 获取会话信息
        session_id = self.memory_manager.current_session.session_id

        state.persona_context = persona_context
        state.conversation_context = conversation_context
        state.session_id = session_id

        print(f"✅ 上下文加载完成，会话ID: {session_id}")
        return state

    async def _analyze_query(self, state: AgentState) -> AgentState:
        """分析用户查询，判断需要执行的操作"""
        print(f"🧠 分析用户查询: {state.user_message[:50]}...")

        user_message = state.user_message

        # 判断查询类型
        query_lower = user_message.lower()

        # 工具调用关键词
        tool_keywords = ["计算", "天气", "计算器", "calculator", "weather"]
        # 记忆检索关键词
        memory_keywords = ["记得", "之前", "历史", "笔记", "记录", "回想起"]

        needs_tools = any(keyword in query_lower for keyword in tool_keywords)
        needs_memory = any(keyword in query_lower for keyword in memory_keywords)

        # 生成搜索查询（用于语义检索）
        search_query = user_message
        if len(user_message) > 100:
            # 截取关键部分
            search_query = user_message[:100] + "..."

        state.search_query = search_query

        # 决定下一步操作
        if needs_tools:
            state.metadata["next_action"] = "tools"
            print("🔧 检测到工具调用需求")
        elif needs_memory:
            state.metadata["next_action"] = "search"
            print("📚 检测到记忆检索需求")
        else:
            state.metadata["next_action"] = "respond"
            print("💬 准备生成回应")

        return state

    def _decide_next_step(self, state: AgentState) -> str:
        """决定下一步操作"""
        return state.metadata.get("next_action", "respond")

    async def _search_notes(self, state: AgentState) -> AgentState:
        """搜索相关笔记"""
        print(f"🔍 搜索相关笔记: {state.search_query[:50]}...")

        try:
            # 执行语义搜索
            search_results = self.vector_store.search(
                query=state.search_query,
                top_k=5,
                min_score=0.2
            )

            state.relevant_notes = search_results
            state.retrieval_results = search_results

            print(f"✅ 找到 {len(search_results)} 条相关笔记")

            # 格式化检索结果
            if search_results:
                notes_text = "相关笔记内容：\n"
                for i, note in enumerate(search_results):
                    notes_text += f"{i+1}. {note['content'][:200]}...\n"
                state.metadata["formatted_notes"] = notes_text

        except Exception as e:
            print(f"❌ 笔记搜索失败: {e}")
            state.relevant_notes = []

        return state

    async def _call_tools(self, state: AgentState) -> AgentState:
        """调用工具"""
        print("🔧 准备调用工具...")

        # 这里可以集成现有的工具系统
        # 暂时返回空结果，后续可以扩展
        state.tool_results = []
        state.metadata["tool_executed"] = False

        print("ℹ️ 工具调用功能待实现")
        return state

    async def _generate_response(self, state: AgentState) -> AgentState:
        """生成个性化回应"""
        print("💭 生成AI回应...")

        # 构建上下文信息
        context_parts = []

        # 画像上下文
        if state.persona_context:
            context_parts.append(f"画像信息：\n{state.persona_context}")

        # 对话上下文
        if state.conversation_context:
            context_parts.append(f"最近对话：\n{state.conversation_context}")

        # 相关笔记
        if state.relevant_notes:
            notes_summary = "相关历史笔记：\n"
            for i, note in enumerate(state.relevant_notes[:3]):  # 最多使用3条笔记
                notes_summary += f"{i+1}. {note['content'][:150]}...\n"
            context_parts.append(notes_summary)

        # 构建完整的上下文
        full_context = "\n\n".join(context_parts) if context_parts else "无特定上下文"

        # 构建系统提示
        system_prompt = f"""你是一个专业的AI开发伙伴，擅长LangGraph框架和智能体开发。

{full_context}

请根据以上信息，提供个性化、专业的回应。注意：
1. 保持专业但友好的语调
2. 自然地引用相关的历史经验和笔记
3. 提供实用的建议和代码示例
4. 保持对话的连贯性和上下文感知
5. 如果用户询问技术问题，给出具体的解决方案

用户消息：{state.user_message}"""

        try:
            # 生成回应
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=state.user_message)
            ]

            response = self.llm.invoke(messages)
            
            # 确保正确获取content
            if isinstance(response, dict) and "content" in response:
                ai_response = response["content"]
            elif hasattr(response, 'content'):
                ai_response = response.content
            else:
                # 兼容其他可能的返回格式
                ai_response = str(response)

            state.ai_response = ai_response
            print(f"✅ 回应生成完成: {ai_response[:100]}...")

        except Exception as e:
            print(f"❌ 回应生成失败: {e}")
            state.ai_response = "抱歉，我在生成回应时遇到了问题。请稍后再试。"

        return state

    async def _update_memory(self, state: AgentState) -> AgentState:
        """更新记忆系统"""
        print("💾 更新记忆系统...")

        try:
            # 添加对话轮次到记忆
            context_used = []

            # 记录使用的上下文
            if state.relevant_notes:
                context_used.extend([f"笔记: {note['content'][:50]}..." for note in state.relevant_notes])

            if state.persona_context:
                context_used.append("用户画像信息")

            success = self.memory_manager.add_conversation_turn(
                user_message=state.user_message,
                ai_response=state.ai_response,
                context_used=context_used,
                tools_called=state.tool_calls,
                search_query=state.search_query,
                retrieval_count=len(state.relevant_notes)
            )

            if success:
                print("✅ 记忆更新成功")
            else:
                print("❌ 记忆更新失败")

        except Exception as e:
            print(f"❌ 记忆更新异常: {e}")

        return state

    async def chat(self, user_message: str) -> str:
        """
        进行对话

        Args:
            user_message: 用户消息

        Returns:
            AI 回应
        """
        print(f"\n🎯 用户消息: {user_message}")
        print("-" * 50)

        try:
            # 初始化状态
            initial_state = AgentState(
                user_message=user_message,
                timestamp=datetime.now()
            )

            # 执行状态图
            config = {"configurable": {"thread_id": self.memory_manager.current_session.session_id}}
            result = await self.graph.ainvoke(initial_state, config=config)

            # 处理不同类型的返回值
            if isinstance(result, dict):
                return result.get("ai_response", "抱歉，未能生成有效的回应。")
            elif hasattr(result, "ai_response"):
                return result.ai_response
            else:
                return "抱歉，回应格式不正确。"

        except Exception as e:
            error_msg = f"对话处理失败: {e}"
            print(f"❌ {error_msg}")
            return f"抱歉，处理您的消息时出现了错误：{error_msg}"

    def get_session_info(self) -> Dict:
        """获取当前会话信息"""
        return {
            "session_id": self.memory_manager.current_session.session_id,
            "vector_store_stats": self.vector_store.get_stats(),
            "memory_stats": self.memory_manager.get_memory_stats(),
            "persona_validation": self.persona_manager.validate_persona_files()
        }

    async def close(self):
        """关闭智能体，清理资源"""
        print("🔚 关闭AI Partner智能体...")

        # 保存最终状态
        self.memory_manager._save_memory()

        print("✅ 资源清理完成")


# 便捷函数
async def create_partner_agent(
    config_dir: str = "./config",
    vector_db_path: str = "./vector_db",
    memory_dir: str = "./memory"
) -> AIPartnerAgent:
    """
    创建AI Partner智能体实例

    Args:
        config_dir: 配置目录
        vector_db_path: 向量数据库路径
        memory_dir: 记忆目录

    Returns:
        智能体实例
    """
    return AIPartnerAgent(config_dir, vector_db_path, memory_dir)


if __name__ == "__main__":
    import asyncio

    async def demo():
        agent = await create_partner_agent()

        # 示例对话
        test_messages = [
            "你好，我想了解一下LangGraph的基本用法",
            "记得我之前提到的Coze项目吗？我想用LangGraph重新实现",
            "你能帮我设计一个智能体的架构吗？"
        ]

        for msg in test_messages:
            response = await agent.chat(msg)
            print(f"\nAI回应: {response}")
            print("\n" + "="*80 + "\n")

        await agent.close()

    asyncio.run(demo())
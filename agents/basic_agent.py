"""
基础LangGraph智能体
演示最简单的智能体创建流程
"""

from typing import Dict, List, Any
from pydantic import BaseModel
from langgraph.graph import StateGraph, END
from utils.llm import get_llm
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentState(BaseModel):
    """智能体状态类型定义"""
    messages: List[Dict[str, Any]]
    current_response: str = ""

def create_basic_agent():
    """
    创建一个基础的对话智能体

    Returns:
        可编译的智能体图
    """
    # 定义智能体节点
    def chat_node(state: AgentState) -> Dict[str, Any]:
        """对话节点：处理用户输入并生成回复"""
        print(f"\n处理消息数量: {len(state.messages)}")
        for msg in state.messages:
            print(f"  - {msg.get('role', 'unknown')}: {msg.get('content', '')[:30]}...")

        try:
            # 获取LLM实例
            llm = get_llm()
            
            # 调用LLM生成回复
            print("正在调用LLM...")
            response = llm.invoke(state.messages)
            print(f"LLM返回结果: {response}")

            # 提取响应内容
            content = response.get("content", "未收到有效响应")
                
            # 准备助手消息
            assistant_message = {
                "role": "assistant",
                "content": content
            }
            
            # 返回更新后的状态
            return {
                "messages": [*state.messages, assistant_message],
                "current_response": content
            }
            
        except Exception as e:
            print(f"\nLLM调用错误: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 错误消息
            error_content = f"很抱歉，我在处理您的请求时遇到了错误: {str(e)}"
            error_message = {
                "role": "assistant",
                "content": error_content
            }
            
            return {
                "messages": [*state.messages, error_message],
                "current_response": error_content
            }

    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("chat", chat_node)

    # 设置入口点
    workflow.set_entry_point("chat")

    # 添加结束边
    workflow.add_edge("chat", END)

    # 编译智能体
    return workflow.compile()

def run_basic_agent():
    """运行基础智能体示例"""
    print("=== LangGraph 基础智能体演示 ===")
    print("输入 'quit' 退出对话\n")

    try:
        # 创建智能体
        agent = create_basic_agent()
        print("智能体创建成功，准备开始对话...")

        # 初始化状态 - 使用新的格式
        initial_state = {
            "messages": [],
            "current_response": ""
        }
        state = AgentState(**initial_state)

        # 为了演示，我们直接提供一个初始的简单问题，避免交互式输入
        print("\n[演示模式] 正在发送测试问题...")
        test_question = "你好，能介绍一下你自己吗？"
        print(f"\n用户: {test_question}")
        
        # 添加用户消息到状态 - 使用字典格式而不是HumanMessage
        user_message = {
            "role": "user",
            "content": test_question
        }
        state.messages.append(user_message)

        # 运行智能体
        print("\n正在处理请求...")
        result = agent.invoke(state)

        # 显示回复
        print(f"\n助手: {result['current_response']}")
        
        print("\n演示完成！您可以修改代码来进行交互式对话。")
        
    except Exception as e:
        print(f"\n运行错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_basic_agent()
"""
AI Partner Chat 完整演示
展示个性化对话、记忆管理和笔记检索功能
"""

import asyncio
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
import sys
sys.path.insert(0, str(project_root))

from agents.partner_agent import create_partner_agent
from scripts.chunk_and_index import IntelligentNoteChunker
from utils.vector_store import VectorStore
from utils.memory_manager import MemoryManager


async def setup_demo_notes():
    """设置演示用的笔记"""
    print("📝 创建演示笔记...")

    notes_dir = Path("./notes")
    notes_dir.mkdir(exist_ok=True)

    # 创建一些演示笔记
    demo_notes = {
        "langgraph_basics.md": """# LangGraph 基础概念

## 核心组件

LangGraph 是一个用于构建有状态、多参与者应用程序的库，特别适合构建AI智能体。

### 状态图
LangGraph 使用有向图来表示应用程序的状态流转：

```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
```

### 检查点机制
检查点可以保存状态，支持暂停和恢复：

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
workflow = workflow.compile(checkpointer=checkpointer)
```

## 应用场景

1. **对话智能体**：维护对话历史和上下文
2. **多步骤任务**：复杂任务的分解和执行
3. **工具调用**：智能选择和调用外部工具
4. **记忆系统**：长期和短期记忆管理

## 优势

- ✅ 状态管理自动化
- ✅ 可视化调试
- ✅ 错误恢复
- ✅ 并行执行支持
""",
        "coze_to_langgraph.md": """# 从 Coze 迁移到 LangGraph 的经验

## 迁移动机

在 Coze 平台开发了一段时间后，发现了一些限制：
- 可视化拖拽虽然方便，但缺乏细粒度控制
- 工具集成受限，无法自定义复杂逻辑
- 状态管理比较基础，难以处理复杂业务流程
- 调试能力有限，难以定位问题

## 迁移过程

### 第一阶段：基础概念学习
花了2-3天时间学习 LangGraph 的核心概念：
- 状态图的理解
- 节点和边的定义
- 条件边的使用
- 检查点机制

### 第二阶段：简单项目实践
重新实现了之前在 Coze 中的简单对话机器人：
```python
# 基础对话智能体
class BasicAgent:
    def __init__(self):
        self.llm = CustomLLM()

    async def chat(self, message):
        # 简单的状态图处理
        pass
```

### 第三阶段：高级功能探索
逐步实现了：
- 工具调用机制
- 记忆系统
- 向量化检索
- 个性化对话

## 遇到的挑战

1. **学习曲线**：相比可视化拖拽，代码开发需要更多时间
2. **调试复杂性**：状态图的调试需要新的思维模式
3. **错误处理**：需要自己处理各种异常情况

## 解决方案

1. **渐进式迁移**：先迁移简单功能，再逐步增加复杂特性
2. **模块化设计**：将复杂功能拆分为独立模块
3. **完善测试**：为每个组件编写单元测试

## 成果

现在可以构建比 Coze 更强大的智能体：
- 完全自定义的业务逻辑
- 高性能的状态管理
- 灵活的工具集成
- 完善的错误处理和恢复
""",
        "ai_partner_ideas.md": """# AI Partner 功能设想

## 核心目标

创建一个真正智能的对话伙伴，能够：
- 记住用户的偏好和历史
- 理解上下文并保持对话连贯性
- 主动提供相关的建议和信息
- 随着使用越来越了解用户

## 功能模块

### 1. 个性化画像
- 用户背景和兴趣
- 沟通风格偏好
- 学习目标和项目
- 互动模式偏好

### 2. 智能记忆
- 短期对话记忆
- 长期知识积累
- 重要事件和决策
- 用户成长轨迹

### 3. 上下文感知
- 当前对话主题
- 相关历史信息
- 项目背景知识
- 时间和环境感知

### 4. 主动协助
- 基于历史的建议
- 相关资源推荐
- 进度跟踪和提醒
- 个性化学习路径

## 技术实现

### 向量化存储
使用 ChromaDB 存储和检索用户的历史笔记和对话

### 状态管理
基于 LangGraph 的状态图管理对话流程

### 个性化引擎
结合用户画像和上下文生成个性化回应

### 记忆系统
分层记忆架构：工作记忆 + 长期记忆 + 语义检索

## 用户体验

1. **初次对话**：建立基础画像，了解用户需求
2. **持续互动**：不断学习和适应，提供更好的服务
3. **深度理解**：基于长期互动，真正理解用户
4. **智能协助**：主动发现问题并提供解决方案

## 发展路线

### 版本 1.0：基础功能
- 基本对话能力
- 简单记忆存储
- 基础画像管理

### 版本 2.0：智能化
- 语义检索
- 上下文理解
- 个性化回应

### 版本 3.0：主动性
- 主动建议
- 智能推荐
- 深度学习

"""
    }

    # 写入笔记文件
    for filename, content in demo_notes.items():
        file_path = notes_dir / filename
        if not file_path.exists():
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ 创建笔记: {filename}")
        else:
            print(f"ℹ️ 笔记已存在: {filename}")


async def initialize_vector_store():
    """初始化向量存储"""
    print("\n🔍 初始化向量存储...")

    try:
        # 检查是否已有数据
        vector_store = VectorStore()
        stats = vector_store.get_stats()

        if stats['total_chunks'] > 0:
            print(f"ℹ️ 向量存储已包含 {stats['total_chunks']} 个块")
            return
        else:
            print("📦 开始索引笔记...")
            # 运行分块和索引
            from scripts.chunk_and_index import main as index_main
            index_main()

    except Exception as e:
        print(f"❌ 初始化向量存储失败: {e}")


async def demo_conversation(agent):
    """演示对话功能"""
    print("\n" + "="*80)
    print("🎯 开始 AI Partner 对话演示")
    print("="*80)

    demo_conversations = [
        {
            "message": "你好！我想了解 LangGraph 的基本概念",
            "context": "基础功能测试"
        },
        {
            "message": "记得我之前提到的从 Coze 迁移的经验吗？我想深入了解 LangGraph 的状态管理",
            "context": "记忆检索测试"
        },
        {
            "message": "我在设计一个 AI Partner 系统，你觉得需要考虑哪些重要功能？",
            "context": "个性化建议测试"
        },
        {
            "message": "你能帮我分析一下我现有的笔记中有关于 LangGraph 的关键信息吗？",
            "context": "笔记检索测试"
        },
        {
            "message": "基于我们之前的对话，你对我有什么建议？",
            "context": "上下文理解测试"
        }
    ]

    for i, conv in enumerate(demo_conversations, 1):
        print(f"\n📍 对话 {i} - {conv['context']}")
        print(f"👤 用户: {conv['message']}")

        try:
            response = await agent.chat(conv['message'])
            print(f"🤖 AI: {response}")
        except Exception as e:
            print(f"❌ 对话失败: {e}")

        print("-" * 60)

        # 短暂延迟，便于观察
        await asyncio.sleep(1)


async def demo_memory_features(agent):
    """演示记忆功能"""
    print("\n" + "="*80)
    print("🧠 记忆功能演示")
    print("="*80)

    try:
        # 获取会话信息
        session_info = agent.get_session_info()
        print(f"📊 当前会话信息:")
        print(f"   会话ID: {session_info['session_id']}")
        print(f"   向量存储: {session_info['vector_store_stats']['total_chunks']} 个块")
        print(f"   对话轮次: {session_info['memory_stats']['current_session_turns']}")

        # 获取对话历史
        memory_manager = agent.memory_manager
        recent_context = memory_manager.get_current_context(max_turns=3)

        print(f"\n💬 最近对话上下文:")
        if recent_context and recent_context != "当前没有活跃的对话会话":
            print(recent_context)
        else:
            print("暂无对话历史")

        # 搜索相关对话
        print(f"\n🔍 搜索相关对话 (关键词: 'LangGraph'):")
        search_results = memory_manager.search_conversations("LangGraph", limit=3)

        if search_results:
            for result in search_results:
                print(f"   {result['timestamp'][:10]}: {result['user_message'][:50]}...")
        else:
            print("   未找到相关对话")

    except Exception as e:
        print(f"❌ 记忆功能演示失败: {e}")


async def demo_vector_search(agent):
    """演示向量搜索功能"""
    print("\n" + "="*80)
    print("🔍 向量搜索功能演示")
    print("="*80)

    test_queries = [
        "LangGraph 的核心概念",
        "从 Coze 平台迁移的经验",
        "AI Partner 系统设计",
        "状态管理机制"
    ]

    for query in test_queries:
        print(f"\n🎯 搜索查询: {query}")
        try:
            results = agent.vector_store.search(query, top_k=3, min_score=0.3)

            if results:
                print(f"✅ 找到 {len(results)} 个相关结果:")
                for i, result in enumerate(results, 1):
                    print(f"   {i}. 相似度: {result['similarity']:.3f}")
                    print(f"      内容: {result['content'][:100]}...")
                    print(f"      来源: {result['metadata']['filename']}")
            else:
                print("❌ 未找到相关结果")

        except Exception as e:
            print(f"❌ 搜索失败: {e}")

        print("-" * 40)


async def main():
    """主演示函数"""
    print("🚀 AI Partner Chat 完整演示开始")

    try:
        # 1. 设置演示笔记
        await setup_demo_notes()

        # 2. 初始化向量存储
        await initialize_vector_store()

        # 3. 创建 AI Partner 智能体
        print("\n🤖 创建 AI Partner 智能体...")
        agent = await create_partner_agent()

        # 4. 显示初始状态
        print("📋 初始状态:")
        session_info = agent.get_session_info()
        print(f"   画像文件: {session_info['persona_validation']}")
        print(f"   会话ID: {session_info['session_id']}")

        # 5. 演示对话功能
        await demo_conversation(agent)

        # 6. 演示记忆功能
        await demo_memory_features(agent)

        # 7. 演示向量搜索
        await demo_vector_search(agent)

        # 8. 清理资源
        print("\n🔚 演示结束，清理资源...")
        await agent.close()

        print("\n🎉 AI Partner Chat 演示完成！")
        print("\n💡 提示:")
        print("   - 你可以修改 config/ 目录下的画像文件来自定义体验")
        print("   - 在 notes/ 目录添加更多笔记来丰富知识库")
        print("   - 使用 scripts/chunk_and_index.py 重新索引笔记")

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 检查环境
    print("🔧 检查环境...")
    if not os.getenv("ZHIPU_API_KEY"):
        print("⚠️ 警告: 未设置 ZHIPU_API_KEY 环境变量")
        print("请设置您的智谱AI API密钥: export ZHIPU_API_KEY=your_key")

    print("✅ 环境检查完成，开始演示...\n")

    asyncio.run(main())
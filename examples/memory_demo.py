"""
记忆功能专项演示
展示对话记忆管理系统的各项功能
"""

import asyncio
from datetime import datetime, timedelta
from pathlib import Path
import sys

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from utils.memory_manager import MemoryManager, ConversationTurn, ConversationSession


async def demo_basic_memory():
    """演示基础记忆功能"""
    print("🧠 基础记忆功能演示")
    print("=" * 50)

    manager = MemoryManager("./demo_memory")

    # 创建会话
    session_id = manager.create_session("demo_session_1")
    print(f"✅ 创建会话: {session_id}")

    # 添加对话轮次
    demo_turns = [
        {
            "user": "你好，我想学习 LangGraph",
            "ai": "很好！LangGraph 是一个强大的智能体框架。你想从哪个方面开始？",
            "context": ["学习计划", "技术框架"],
            "tools": []
        },
        {
            "user": "我想先了解状态图的概念",
            "ai": "状态图是 LangGraph 的核心概念，它用有向图来表示应用状态的变化。每个节点代表一个状态，边代表状态转移。",
            "context": ["状态图", "核心概念"],
            "tools": []
        },
        {
            "user": "能给我一个简单的例子吗？",
            "ai": "当然！我们可以创建一个简单的对话智能体：首先定义状态，然后添加节点，最后设置转移条件。",
            "context": ["代码示例", "实践应用"],
            "tools": []
        }
    ]

    for i, turn in enumerate(demo_turns, 1):
        print(f"\n📝 添加对话轮次 {i}:")
        success = manager.add_conversation_turn(
            user_message=turn["user"],
            ai_response=turn["ai"],
            context_used=turn["context"],
            tools_called=turn["tools"]
        )
        print(f"   {'✅' if success else '❌'} 添加: {turn['user'][:30]}...")

    # 获取对话上下文
    print(f"\n💬 当前对话上下文:")
    context = manager.get_current_context(max_turns=5)
    print(context)

    return manager


async def demo_session_management(manager: MemoryManager):
    """演示会话管理"""
    print("\n\n🔄 会话管理演示")
    print("=" * 50)

    # 创建多个会话
    sessions = []
    for i in range(3):
        session_id = manager.create_session(f"session_{i+1}")
        sessions.append(session_id)
        print(f"✅ 创建会话: {session_id}")

        # 添加一些对话
        manager.add_conversation_turn(
            user_message=f"这是会话 {i+1} 的第一条消息",
            ai_response=f"收到！这是会话 {i+1} 的回应。",
            session_topic=f"主题 {i+1}"
        )

    # 列出所有会话
    print(f"\n📋 所有会话列表:")
    session_list = manager.list_sessions()
    for session_info in session_list:
        print(f"   {session_info['session_id']}: {session_info['total_turns']} 轮对话, "
              f"最后更新: {session_info['last_update'][:10]}")

    # 切换会话
    print(f"\n🔄 切换会话演示:")
    original_session = manager.current_session.session_id

    for session_id in sessions:
        success = manager.switch_session(session_id)
        current_info = manager.get_session_info()
        print(f"   {'✅' if success else '❌'} 切换到 {session_id}: "
              f"{current_info['total_turns']} 轮对话")

    # 切换回原会话
    manager.switch_session(original_session)
    print(f"   🔄 切换回原会话: {original_session}")


async def demo_conversation_search(manager: MemoryManager):
    """演示对话搜索"""
    print("\n\n🔍 对话搜索演示")
    print("=" * 50)

    # 添加更多测试对话
    test_conversations = [
        {
            "user": "LangGraph 的检查点机制如何工作？",
            "ai": "检查点机制允许你保存状态图的中间状态，支持暂停和恢复执行。"
        },
        {
            "user": "如何处理工具调用中的错误？",
            "ai": "可以通过条件边和错误处理节点来捕获和处理工具调用异常。"
        },
        {
            "user": "什么是状态图的条件边？",
            "ai": "条件边基于当前状态决定下一个要执行的节点，实现智能的流程控制。"
        },
        {
            "user": "如何优化 LangGraph 应用的性能？",
            "ai": "可以通过并行执行、状态压缩和智能缓存来优化性能。"
        }
    ]

    for conv in test_conversations:
        manager.add_conversation_turn(
            user_message=conv["user"],
            ai_response=conv["ai"],
            keywords=conv["user"].split()[:3]  # 提取关键词
        )

    # 执行各种搜索
    search_queries = [
        "LangGraph",
        "检查点",
        "错误处理",
        "性能优化"
    ]

    for query in search_queries:
        print(f"\n🔍 搜索: '{query}'")
        results = manager.search_conversations(query, limit=3)

        if results:
            print(f"   找到 {len(results)} 条相关对话:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['timestamp'][:19]}")
                print(f"      用户: {result['user_message']}")
                print(f"      AI: {result['ai_response'][:50]}...")
        else:
            print("   未找到相关对话")


async def demo_memory_statistics(manager: MemoryManager):
    """演示记忆统计"""
    print("\n\n📊 记忆统计演示")
    print("=" * 50)

    # 获取详细统计
    stats = manager.get_memory_stats()
    print("📈 记忆系统统计:")
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # 获取当前会话详情
    current_info = manager.get_session_info()
    if current_info:
        print(f"\n🎯 当前会话详情:")
        print(f"   会话ID: {current_info['session_id']}")
        print(f"   开始时间: {current_info['start_time'][:19]}")
        print(f"   最后更新: {current_info['last_update'][:19]}")
        print(f"   对话轮次: {current_info['total_turns']}")
        print(f"   持续时间: {current_info['duration_minutes']:.1f} 分钟")

    # 显示会话分布
    sessions = manager.list_sessions()
    if sessions:
        print(f"\n📊 会话分布分析:")
        total_turns = sum(s['total_turns'] for s in sessions)
        avg_turns = total_turns / len(sessions)
        max_turns = max(s['total_turns'] for s in sessions)
        min_turns = min(s['total_turns'] for s in sessions)

        print(f"   总会话数: {len(sessions)}")
        print(f"   总对话轮次: {total_turns}")
        print(f"   平均轮次/会话: {avg_turns:.1f}")
        print(f"   最多轮次: {max_turns}")
        print(f"   最少轮次: {min_turns}")


async def demo_advanced_features():
    """演示高级功能"""
    print("\n\n🚀 高级功能演示")
    print("=" * 50)

    manager = MemoryManager("./demo_memory")

    # 演示元数据使用
    print("📝 元数据功能演示:")
    manager.add_conversation_turn(
        user_message="我想了解 LangGraph 的高级特性",
        ai_response="LangGraph 的高级特性包括并行执行、条件路由、子图等。",
        complexity="advanced",
        topic="advanced_features",
        user_skill_level="intermediate",
        estimated_time="15 minutes",
        related_concepts=["parallel_execution", "conditional_routing"]
    )

    # 演示带丰富元数据的搜索
    print("\n🔍 基于元数据的分析:")
    recent_turns = manager.current_session.get_recent_turns(1)
    if recent_turns:
        last_turn = recent_turns[0]
        print(f"   最后一轮对话元数据:")
        for key, value in last_turn.metadata.items():
            print(f"     {key}: {value}")

    # 演示上下文摘要功能
    print("\n📋 上下文摘要:")
    summary = manager.current_session.get_context_summary(max_turns=5)
    print(summary)


async def demo_cleanup_and_maintenance():
    """演示清理和维护功能"""
    print("\n\n🧹 清理和维护演示")
    print("=" * 50)

    manager = MemoryManager("./demo_memory")

    # 创建一些旧会话
    old_date = datetime.now() - timedelta(days=35)

    # 手动创建一些历史会话（模拟旧数据）
    old_session = ConversationSession(
        session_id="old_session_1",
        start_time=old_date,
        last_update=old_date,
        turns=[
            ConversationTurn(
                timestamp=old_date,
                user_message="这是很久以前的对话",
                ai_response="确实是很久以前的对话"
            )
        ]
    )
    manager.sessions["old_session_1"] = old_session

    print(f"📊 清理前统计:")
    before_stats = manager.get_memory_stats()
    print(f"   总会话数: {before_stats['total_sessions']}")

    # 清理旧会话
    print(f"\n🧹 清理30天前的会话...")
    cleared_count = manager.clear_old_sessions(days=30)
    print(f"✅ 清理了 {cleared_count} 个旧会话")

    print(f"\n📊 清理后统计:")
    after_stats = manager.get_memory_stats()
    print(f"   总会话数: {after_stats['total_sessions']}")


async def main():
    """主演示函数"""
    print("🚀 记忆功能专项演示开始\n")

    try:
        # 1. 基础记忆功能
        manager = await demo_basic_memory()

        # 2. 会话管理
        await demo_session_management(manager)

        # 3. 对话搜索
        await demo_conversation_search(manager)

        # 4. 记忆统计
        await demo_memory_statistics(manager)

        # 5. 高级功能
        await demo_advanced_features()

        # 6. 清理和维护
        await demo_cleanup_and_maintenance()

        print("\n🎉 记忆功能演示完成！")
        print("\n💡 主要特性:")
        print("   ✅ 多会话管理")
        print("   ✅ 智能对话搜索")
        print("   ✅ 丰富的元数据支持")
        print("   ✅ 自动清理和维护")
        print("   ✅ 详细的统计分析")

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
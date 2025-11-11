"""
多会话上下文保持演示
展示 AI Partner 在多个会话中保持上下文连贯性的能力
"""

import asyncio
from pathlib import Path
import sys
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.partner_agent import create_partner_agent
from utils.memory_manager import MemoryManager


async def simulate_user_sessions():
    """模拟用户在多个会话中的对话"""
    print("🎭 多会话场景模拟")
    print("=" * 60)

    # 创建 AI Partner 智能体
    agent = await create_partner_agent()

    # 模拟多个对话会话
    sessions = [
        {
            "name": "学习 LangGraph 基础",
            "topic": "LangGraph 入门",
            "conversations": [
                "你好，我想开始学习 LangGraph，应该从哪里开始？",
                "LangGraph 和其他 AI 框架有什么区别？",
                "能给我推荐一些学习资源吗？",
                "我想创建我的第一个 LangGraph 应用，有什么建议？"
            ]
        },
        {
            "name": "项目实践讨论",
            "topic": "智能体项目开发",
            "conversations": [
                "我正在开发一个客户服务智能体，遇到了一些问题",
                "如何处理复杂的用户查询？",
                "集成了外部工具后，响应变慢了，怎么优化？",
                "测试时发现了一些边界情况，应该如何处理？"
            ]
        },
        {
            "name": "高级特性探索",
            "topic": "高级功能实现",
            "conversations": [
                "我想实现智能体的记忆功能，有什么建议？",
                "如何在 LangGraph 中实现并行执行？",
                "状态图的检查点机制具体怎么使用？",
                "能解释一下条件边的工作原理吗？"
            ]
        }
    ]

    session_contexts = {}

    # 逐个会话进行对话
    for i, session in enumerate(sessions, 1):
        session_name = session["name"]
        topic = session["topic"]
        conversations = session["conversations"]

        print(f"\n📍 会话 {i}: {session_name}")
        print(f"🎯 主题: {topic}")
        print("-" * 40)

        # 创建新会话
        session_id = agent.memory_manager.create_session(f"session_{int(time.time())}")
        session_contexts[session_name] = {
            "session_id": session_id,
            "topic": topic,
            "key_points": []
        }

        print(f"💬 开始对话 (会话ID: {session_id[:8]}...)")

        # 进行多轮对话
        for j, user_msg in enumerate(conversations, 1):
            print(f"\n👤 用户轮次 {j}: {user_msg}")

            try:
                # 发送消息并获取回应
                ai_response = await agent.chat(user_msg)
                print(f"🤖 AI 回应: {ai_response[:200]}{'...' if len(ai_response) > 200 else ''}")

                # 记录关键点
                if any(keyword in user_msg.lower() for keyword in ["如何", "怎么", "建议", "推荐"]):
                    session_contexts[session_name]["key_points"].append({
                        "round": j,
                        "question": user_msg,
                        "answer": ai_response[:100] + "..."
                    })

                # 短暂延迟，模拟真实对话
                await asyncio.sleep(0.5)

            except Exception as e:
                import traceback
                print(f"❌ 对话失败: {e}")
                print("完整错误堆栈:")
                traceback.print_exc()

        print(f"\n✅ 会话 {i} 完成，共进行 {len(conversations)} 轮对话")

    return agent, session_contexts


async def demonstrate_context_switching(agent, session_contexts):
    """演示上下文切换和记忆关联"""
    print("\n\n🔄 上下文切换演示")
    print("=" * 60)

    print("演示智能体在不同会话间切换并保持关联性...")

    # 在不同会话间切换并测试记忆
    cross_session_questions = [
        {
            "session": "学习 LangGraph 基础",
            "question": "记得我之前问过 LangGraph 的区别吗？能再详细解释一下？",
            "expected_context": "应该回忆起之前关于框架区别的讨论"
        },
        {
            "session": "项目实践讨论",
            "question": "我之前提到的客户服务智能体问题，后来有什么新的解决方案吗？",
            "expected_context": "应该关联到之前的项目开发问题"
        },
        {
            "session": "高级特性探索",
            "question": "结合我之前讨论的并行执行和检查点，能给我一个完整的示例吗？",
            "expected_context": "应该结合两个不同的高级功能讨论"
        }
    ]

    for i, test_case in enumerate(cross_session_questions, 1):
        session_name = test_case["session"]
        question = test_case["question"]
        expected = test_case["expected_context"]

        print(f"\n🎯 测试 {i}: {session_name}")
        print(f"❓ 问题: {question}")
        print(f"🎯 期望: {expected}")

        # 切换到指定会话
        session_info = session_contexts[session_name]
        success = agent.memory_manager.switch_session(session_info["session_id"])
        print(f"🔄 会话切换: {'✅ 成功' if success else '❌ 失败'}")

        if success:
            try:
                # 发送跨会话问题
                ai_response = await agent.chat(question)
                print(f"🤖 AI 回应: {ai_response[:250]}{'...' if len(ai_response) > 250 else ''}")

                # 分析回应是否体现了上下文关联
                context_indicators = ["之前", "记得", "刚才", "前面", "结合", "基于"]
                has_context = any(indicator in ai_response for indicator in context_indicators)
                print(f"📊 上下文关联: {'✅ 检测到' if has_context else '⚠️ 未明显检测到'}")

            except Exception as e:
                print(f"❌ 处理失败: {e}")

        print("-" * 40)


async def demonstrate_memory_integration(agent, session_contexts):
    """演示记忆整合功能"""
    print("\n\n🧠 记忆整合演示")
    print("=" * 60)

    print("分析所有会话中的关键信息...")

    # 收集所有会话的关键点
    all_key_points = []
    for session_name, context in session_contexts.items():
        print(f"\n📋 会话: {session_name}")
        key_points = context["key_points"]
        print(f"   关键点数量: {len(key_points)}")

        for point in key_points:
            all_key_points.append({
                "session": session_name,
                "round": point["round"],
                "question": point["question"],
                "answer": point["answer"]
            })
            print(f"   轮次 {point['round']}: {point['question'][:50]}...")

    # 生成综合性问题测试记忆整合
    integration_questions = [
        "综合我们之前所有的讨论，你能总结一下我的学习路径吗？",
        "我首先学习了 LangGraph 基础，然后讨论了项目实践，最后探索了高级特性，下一步应该重点关注什么？",
        "基于我在不同会话中提到的问题，你觉得我在学习 LangGraph 时的主要挑战是什么？",
        "你还记得我在三个不同会话中提到的具体技术问题吗？能帮我梳理一下吗？"
    ]

    print(f"\n🎯 记忆整合测试:")
    print(f"   总会话数: {len(session_contexts)}")
    print(f"   总关键点: {len(all_key_points)}")

    # 切换到一个新会话进行整合测试
    agent.memory_manager.create_session("integration_test")

    for i, question in enumerate(integration_questions, 1):
        print(f"\n💬 整合问题 {i}: {question}")

        try:
            response = await agent.chat(question)
            print(f"🤖 AI 回应: {response[:300]}{'...' if len(response) > 300 else ''}")

            # 分析回应的整合性
            session_references = ["学习", "项目", "高级", "基础", "实践"]
            reference_count = sum(1 for ref in session_references if ref in response)
            print(f"📊 整合程度: 检测到 {reference_count} 个会话主题的引用")

        except Exception as e:
            print(f"❌ 处理失败: {e}")

        await asyncio.sleep(0.5)


async def demonstrate_session_statistics(agent, session_contexts):
    """演示会话统计分析"""
    print("\n\n📊 会话统计分析")
    print("=" * 60)

    # 获取记忆管理器
    memory_manager = agent.memory_manager

    # 列出所有会话
    all_sessions = memory_manager.list_sessions()
    print(f"📈 会话统计:")
    print(f"   总会话数: {len(all_sessions)}")

    # 分析会话分布
    session_types = {}
    total_turns = 0
    total_duration = 0

    for session_info in all_sessions:
        turns = session_info['total_turns']
        total_turns += turns

        # 获取会话详细信息
        detailed_info = memory_manager.get_session_info(session_info['session_id'])
        if detailed_info:
            duration = detailed_info.get('duration_minutes', 0)
            total_duration += duration

        # 分类会话类型
        session_id = session_info['session_id']
        if 'session_' in session_id:
            session_types['regular'] = session_types.get('regular', 0) + 1
        elif 'integration' in session_id:
            session_types['integration'] = session_types.get('integration', 0) + 1
        else:
            session_types['other'] = session_types.get('other', 0) + 1

    print(f"   总对话轮次: {total_turns}")
    print(f"   总对话时长: {total_duration:.1f} 分钟")
    print(f"   平均轮次/会话: {total_turns / len(all_sessions):.1f}")
    print(f"   平均时长/会话: {total_duration / len(all_sessions):.1f} 分钟")

    print(f"\n📋 会话类型分布:")
    for session_type, count in session_types.items():
        print(f"   {session_type}: {count} 个会话")

    # 搜索统计
    print(f"\n🔍 对话搜索测试:")
    search_terms = ["LangGraph", "智能体", "问题", "学习"]
    for term in search_terms:
        results = memory_manager.search_conversations(term, limit=5)
        print(f"   '{term}': {len(results)} 条相关对话")


async def main():
    """主演示函数"""
    print("🚀 多会话上下文保持演示开始\n")

    try:
        # 1. 模拟多个用户会话
        agent, session_contexts = await simulate_user_sessions()

        # 2. 演示上下文切换
        await demonstrate_context_switching(agent, session_contexts)

        # 3. 演示记忆整合
        await demonstrate_memory_integration(agent, session_contexts)

        # 4. 演示统计分析
        await demonstrate_session_statistics(agent, session_contexts)

        # 清理资源
        print(f"\n🔚 演示结束，清理资源...")
        await agent.close()

        print(f"\n🎉 多会话演示完成！")
        print(f"\n💡 演示要点:")
        print(f"   ✅ 多会话创建和管理")
        print(f"   ✅ 会话间上下文切换")
        print(f"   ✅ 跨会话记忆关联")
        print(f"   ✅ 对话内容整合")
        print(f"   ✅ 会话统计分析")

    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🔧 环境检查...")
    print("✅ 开始多会话演示...\n")

    asyncio.run(main())
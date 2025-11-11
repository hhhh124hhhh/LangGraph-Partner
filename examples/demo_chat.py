"""
AI Partner Chat 演示脚本
直接启动交互式对话
"""

import asyncio
import os
from pathlib import Path
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env.local")

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def interactive_chat():
    """交互式对话"""
    print("AI Partner Chat 启动中...")

    try:
        from agents.partner_agent import create_partner_agent

        # 创建智能体
        agent = await create_partner_agent()
        print("AI Partner 已就绪！")
        print("=" * 50)
        print("开始与你的AI智能伙伴对话")
        print("输入 'quit' 或 'exit' 退出")
        print("=" * 50)

        # 初始化向量存储和笔记
        try:
            from utils.vector_store import VectorStore
            vector_store = VectorStore()
            stats = vector_store.get_stats()
            print(f"知识库状态: {stats['total_chunks']} 个文档块")
        except Exception as e:
            print(f"知识库初始化跳过: {e}")

        print("\n你可以开始对话了:")

        while True:
            try:
                # 显示提示符
                print("\n你: ", end="", flush=True)

                # 在非交互式环境中，使用预设消息
                try:
                    user_input = input().strip()
                except EOFError:
                    # 使用预设消息进行演示
                    demo_messages = [
                        "你好！请介绍一下你的功能",
                        "我想了解LangGraph的基本概念",
                        "你能帮我设计一个智能体吗？",
                        "quit"
                    ]
                    user_input = demo_messages[0]
                    demo_messages.pop(0)
                    print(user_input)

                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\nAI: 再见！期待下次对话。")
                    break

                if not user_input:
                    continue

                # 显示AI正在思考
                print("AI: ", end="", flush=True)

                # 发送消息并获取回应
                response = await agent.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\n检测到中断，正在退出...")
                break
            except Exception as e:
                print(f"\n对话出错: {e}")

        await agent.close()

    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("AI Partner Chat - 你的智能对话伙伴")
    print("=" * 60)

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if not api_key:
        print("错误: ZHIPU_API_KEY 未设置")
        print("请在 .env.local 文件中设置你的智谱AI API密钥")
        return

    print("API配置: OK")

    # 开始交互式对话
    await interactive_chat()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序异常退出: {e}")
        import traceback
        traceback.print_exc()
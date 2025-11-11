"""
AI Partner Chat 启动脚本
简化版本，避免编码问题
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


def check_environment():
    """检查环境配置"""
    print("环境检查")
    print("-" * 30)

    # 检查 API 密钥
    api_key = os.getenv("ZHIPU_API_KEY")
    if api_key:
        print("OK: ZHIPU_API_KEY 已设置")
        return True
    else:
        print("ERROR: ZHIPU_API_KEY 未设置")
        print("请设置环境变量: set ZHIPU_API_KEY=your_api_key")
        return False


async def test_ai_partner():
    """测试 AI Partner 功能"""
    print("\nAI Partner 功能测试")
    print("-" * 30)

    try:
        from agents.partner_agent import create_partner_agent

        print("创建 AI Partner 智能体...")
        agent = await create_partner_agent()

        print("智能体创建成功")

        # 获取会话信息
        session_info = agent.get_session_info()
        print(f"会话ID: {session_info['session_id'][:8]}...")

        # 测试简单对话
        print("\n测试对话功能...")
        test_message = "你好！请简单介绍一下你的功能。"

        response = await agent.chat(test_message)
        print(f"用户: {test_message}")
        print(f"AI: {response}")

        # 关闭智能体
        await agent.close()
        print("功能测试通过")
        return True

    except Exception as e:
        print(f"功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def interactive_chat():
    """交互式对话"""
    print("\n开始交互式对话")
    print("输入 'quit' 或 'exit' 退出")
    print("-" * 40)

    try:
        from agents.partner_agent import create_partner_agent

        agent = await create_partner_agent()

        print("\nAI Partner 已就绪！开始对话吧...\n")

        while True:
            try:
                # 获取用户输入
                user_input = input("用户: ").strip()

                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("再见！")
                    break

                if not user_input:
                    continue

                # 发送消息并获取回应
                print("AI: ", end="", flush=True)
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
    print("AI Partner Chat 启动")
    print("=" * 50)

    # 1. 环境检查
    if not check_environment():
        print("\n环境检查失败，请解决上述问题后重试")
        return

    # 2. 功能测试
    print("\n是否进行功能测试? (y/n): ", end="")
    test_choice = input().strip().lower()

    if test_choice in ['y', 'yes', '是', '']:
        if not await test_ai_partner():
            print("\n功能测试失败")
            return
        print("\n功能测试通过！")

    # 3. 交互式对话
    await interactive_chat()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户取消，启动中断")
    except Exception as e:
        print(f"\n启动过程中出现未预期的错误: {e}")
        import traceback
        traceback.print_exc()
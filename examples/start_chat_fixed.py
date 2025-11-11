"""
AI Partner Chat 启动脚本 - 修复编码版本
解决 Windows 终端乱码问题
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 设置控制台编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
    # Windows 控制台设置
    os.system('chcp 65001 > nul')

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env.local")

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_header(text):
    """打印漂亮的标题"""
    border = "=" * len(text)
    print(border)
    print(text)
    print(border)


def print_section(title):
    """打印章节标题"""
    print(f"\n{'-' * 20} {title} {'-' * 20}")


class SimpleChatAgent:
    """简化版聊天智能体"""

    def __init__(self):
        from utils.llm import CustomLLM
        self.llm = CustomLLM()
        print("Simple AI Partner initialized")
        print("Note: Current version skips vectorization and memory features")

    async def chat(self, message: str) -> str:
        """简单的对话功能"""
        try:
            # 构建简单的对话上下文
            system_prompt = """You are a professional AI development partner specializing in LangGraph framework and agent development.

Please provide professional and friendly responses, focusing on:
1. LangGraph technical questions
2. Agent development suggestions
3. Code examples and practical guidance

User message: """ + message

            from langchain_core.messages import SystemMessage, HumanMessage

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            return f"Sorry, an error occurred while processing your message: {str(e)}"


async def interactive_chat():
    """交互式对话"""
    print_header("AI Partner Chat - Simplified Version")
    print("Note: This is a simplified version without vectorization and memory features")

    print_section("Status Check")

    try:
        from utils.llm import CustomLLM
        llm = CustomLLM()
        print(f"✓ LLM Model: {llm.model_name}")
        print(f"✓ Temperature: {llm.temperature}")
        print(f"✓ API Key: {'*' * 8}{llm.api_key[-4:] if llm.api_key else 'Not set'}")

        agent = SimpleChatAgent()

        print_section("Chat Started")
        print("AI Partner is ready! Start your conversation.")
        print("Type 'quit', 'exit', or 'q' to exit")
        print("-" * 50)

        while True:
            try:
                # 获取用户输入
                print("\nYou: ", end="", flush=True)

                try:
                    user_input = input().strip()
                except EOFError:
                    # 使用预设演示消息
                    demo_messages = [
                        "Hello! Please introduce LangGraph",
                        "How do I create a simple agent?",
                        "What are the differences between LangGraph and other frameworks?",
                        "quit"
                    ]
                    if not hasattr(interactive_chat, 'demo_index'):
                        interactive_chat.demo_index = 0
                    user_input = demo_messages[interactive_chat.demo_index]
                    interactive_chat.demo_index += 1
                    print(user_input)

                if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                    print("\nAI: Goodbye! Looking forward to our next conversation.")
                    break

                if not user_input:
                    continue

                # 显示AI正在思考
                print("AI: ", end="", flush=True)

                # 发送消息并获取回应
                response = await agent.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                print("\n\nInterrupt detected, exiting...")
                break
            except Exception as e:
                print(f"\nChat error: {e}")

    except Exception as e:
        print(f"Startup failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print_header("AI Partner Chat Launch")

    print_section("Environment Check")

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ ERROR: API key not set")
        print("Please set your API key in .env.local file")
        return

    print("✓ API Configuration: OK")

    print_section("Starting AI Partner")

    # 开始交互式对话
    await interactive_chat()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        print(f"\nProgram exited with error: {e}")
        import traceback
        traceback.print_exc()
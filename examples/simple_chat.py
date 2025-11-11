"""
AI Partner Chat 简化版演示
暂时跳过向量化功能，专注于基本对话
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


class SimpleChatAgent:
    """简化版聊天智能体"""

    def __init__(self):
        from utils.llm import CustomLLM
        self.llm = CustomLLM()
        print("简化版 AI Partner 已初始化")
        print("注意：当前版本跳过了向量化和记忆功能")

    async def chat(self, message: str) -> str:
        """简单的对话功能"""
        try:
            # 构建简单的对话上下文
            system_prompt = """你是一个专业的AI开发伙伴，擅长LangGraph框架和智能体开发。

请提供专业、友好的回应，重点关注：
1. LangGraph 技术问题
2. 智能体开发建议
3. 代码示例和实践指导

用户消息：""" + message

            from langchain_core.messages import SystemMessage, HumanMessage

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]

            response = self.llm.invoke(messages)
            return response.content

        except Exception as e:
            return f"抱歉，处理您的消息时出现错误：{str(e)}"


async def interactive_chat():
    """交互式对话"""
    print("AI Partner Chat 简化版启动")
    print("=" * 50)
    print("注意：这是简化版本，暂不包含向量化和记忆功能")
    print("=" * 50)

    try:
        agent = SimpleChatAgent()

        print("\nAI Partner 已就绪！开始对话吧:")
        print("输入 'quit' 或 'exit' 退出")
        print("-" * 40)

        while True:
            try:
                # 获取用户输入
                print("\n你: ", end="", flush=True)

                try:
                    user_input = input().strip()
                except EOFError:
                    # 使用预设演示消息
                    demo_messages = [
                        "你好！请介绍一下 LangGraph",
                        "如何创建一个简单的智能体？",
                        "LangGraph 和其他框架有什么区别？",
                        "quit"
                    ]
                    if not hasattr(interactive_chat, 'demo_index'):
                        interactive_chat.demo_index = 0
                    user_input = demo_messages[interactive_chat.demo_index]
                    interactive_chat.demo_index += 1
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

    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主函数"""
    print("AI Partner Chat 简化版")
    print("=" * 40)

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("错误: API密钥未设置")
        print("请在 .env.local 文件中设置你的API密钥")
        return

    print("API配置: OK")

    # 显示LLM配置
    from utils.llm import CustomLLM
    llm = CustomLLM()
    print(f"LLM模型: {llm.model_name}")
    print(f"温度: {llm.temperature}")

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
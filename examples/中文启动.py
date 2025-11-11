"""
AI Partner Chat 中文启动脚本
完全中文化的交互体验
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


class 中文AI助手:
    """中文AI助手"""

    def __init__(self):
        from utils.llm import CustomLLM
        self.llm = CustomLLM()
        print("中文AI智能助手已初始化")
        print("说明：当前为简化版本，暂不包含向量化和记忆功能")

    async def 对话(self, 消息: str) -> str:
        """对话功能"""
        try:
            # 构建中文对话上下文
            系统提示 = """你是一个专业的AI开发伙伴，专精于LangGraph框架和智能体开发。

请提供专业、友好的中文回应，重点关注：
1. LangGraph技术问题的解答
2. 智能体开发建议和指导
3. 代码示例和实际应用
4. 用中文清晰地解释复杂概念

用户消息：""" + 消息

            from langchain_core.messages import SystemMessage, HumanMessage

            消息列表 = [
                SystemMessage(content=系统提示),
                HumanMessage(content=消息)
            ]

            响应 = self.llm.invoke(消息列表)
            return 响应.content

        except Exception as e:
            return f"抱歉，处理您的消息时出现错误：{str(e)}"


async def 中文对话():
    """中文交互式对话"""
    print_header("AI智能伙伴 - 中文版")
    print("说明：这是一个简化版本，不包含向量化和记忆功能")

    print_section("状态检查")

    try:
        from utils.llm import CustomLLM
        llm = CustomLLM()
        print(f"✓ 语言模型: {llm.model_name}")
        print(f"✓ 温度设置: {llm.temperature}")
        print(f"✓ API密钥: {'*' * 8}{llm.api_key[-4:] if llm.api_key else '未设置'}")

        助手 = 中文AI助手()

        print_section("开始对话")
        print("AI智能伙伴已准备就绪！请开始您的对话。")
        print("输入 '退出', 'quit', 'q' 或按 Ctrl+C 结束对话")
        print("-" * 50)

        # 中文演示问题
        演示问题 = [
            "你好，请介绍一下LangGraph是什么？",
            "如何用LangGraph创建一个简单的智能体？",
            "LangGraph相比其他框架有什么优势？",
            "退出"
        ]
        问题索引 = 0

        while True:
            try:
                # 获取用户输入
                print("\n您: ", end="", flush=True)

                try:
                    用户输入 = input().strip()
                except EOFError:
                    # 使用演示问题
                    if 问题索引 < len(演示问题):
                        用户输入 = 演示问题[问题索引]
                        问题索引 += 1
                        print(用户输入)
                    else:
                        break

                if 用户输入.lower() in ['退出', 'quit', 'exit', 'q']:
                    print("\nAI: 再见！期待我们的下次对话。")
                    break

                if not 用户输入:
                    continue

                # 显示AI正在思考
                print("AI: ", end="", flush=True)

                # 发送消息并获取回应
                回应 = await 助手.对话(用户输入)
                print(回应)

                # 短暂延迟
                await asyncio.sleep(0.5)

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
    print_header("AI智能伙伴启动")

    print_section("环境检查")

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：API密钥未设置")
        print("请在 .env.local 文件中设置您的API密钥")
        return

    print("✓ API配置：正常")

    print_section("启动智能伙伴")

    # 开始中文对话
    await 中文对话()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"\n程序异常退出: {e}")
        import traceback
        traceback.print_exc()
"""
AI Partner Chat 优化启动脚本
清理调试信息，优化格式，提供更好的用户体验
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
    os.system('chcp 65001 > nul')

# 加载环境变量
load_dotenv(Path(__file__).parent.parent / ".env.local")

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def print_banner():
    """打印程序横幅"""
    print("""
    ╔════════════════════════════════════════════════╗
    ║         AI 智能伙伴 - LangGraph 专家助手         ║
    ║                                                  ║
    ║  🚀 专业的LangGraph技术支持和开发指导           ║
    ║  💬 智能对话，个性化问答体验                   ║
    ║  🎯 中文交互，清晰易懂的技术解释               ║
    ╚════════════════════════════════════════════════╝
    """)


class 优化AI助手:
    """优化格式的AI助手"""

    def __init__(self, silent_init=True):
        """静默初始化，避免调试信息污染界面"""
        from utils.llm import CustomLLM
        if not silent_init:
            print("正在初始化AI智能助手...")
        self.llm = CustomLLM()
        if not silent_init:
            print("✓ AI助手初始化完成")

    def _clean_debug_output(self, text):
        """清理调试信息，只保留用户需要的内容"""
        # 移除常见的调试信息
        debug_patterns = [
            "CustomLLM调用中，消息数量:",
            "API响应类型:",
            "API响应:",
            "成功提取响应内容:",
            "环境变量加载状态:",
            "创建CustomLLM实例:",
        ]

        lines = text.split('\n')
        cleaned_lines = []
        skip_next = False

        for line in lines:
            line = line.strip()

            # 跳过调试信息行
            if any(pattern in line for pattern in debug_patterns):
                skip_next = True
                continue

            # 跳过模型信息和API密钥信息
            if skip_next or "模型:" in line or "温度:" in line or "API密钥:" in line or "基础URL:" in line:
                skip_next = False
                continue

            # 跳过错误信息，保留有效内容
            if line.startswith("抱歉") or line.startswith("Sorry") or "dict' object has no attribute" in line:
                continue

            # 保留有效内容
            if line:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _format_response(self, response):
        """格式化AI回应，使其更易读"""
        # 清理调试信息
        cleaned = self._clean_debug_output(response)

        # 移除多余的空白行
        lines = cleaned.split('\n')
        formatted_lines = []
        prev_empty = False

        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
                prev_empty = False
            elif not prev_empty:
                formatted_lines.append("")
                prev_empty = True

        return '\n'.join(formatted_lines)

    async def 对话(self, 消息: str) -> str:
        """格式化的对话功能"""
        try:
            # 构建系统提示
            系统提示 = """你是一个专业的AI开发伙伴，专精于LangGraph框架和智能体开发。

请提供专业、友好的中文回应，重点关注：
1. LangGraph技术问题的清晰解答
2. 智能体开发的实用建议
3. 代码示例和实际应用指导
4. 用中文准确解释复杂概念

回答要求：
- 语言简洁明了，避免过于冗长
- 结构清晰，适当使用段落分隔
- 重点关注实用性和可操作性
- 保持专业但友好的语调

用户消息：""" + 消息

            from langchain_core.messages import SystemMessage, HumanMessage

            消息列表 = [
                SystemMessage(content=系统提示),
                HumanMessage(content=消息)
            ]

            响应 = self.llm.invoke(消息列表)

            # 格式化回应
            格式化回应 = self._format_response(响应.content)

            return 格式化回应 if 格式化回应 else "抱歉，我无法提供有效的回应。"

        except Exception as e:
            return f"抱歉，处理您的消息时出现错误：{str(e)}"


async def 优化对话():
    """优化的交互式对话"""
    print_banner()

    print("🔧 正在检查环境...")

    # 检查API密钥
    api_key = os.getenv("ZHIPU_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ 错误：API密钥未设置")
        print("请在 .env.local 文件中设置您的API密钥")
        return

    print("✅ 环境检查通过")
    print("🚀 正在启动AI智能伙伴...")

    try:
        # 静默初始化助手
        助手 = 优化AI助手(silent_init=True)

        print("✅ AI智能伙伴已准备就绪")
        print("\n" + "="*60)
        print("💬 开始您的对话体验")
        print("💡 输入 '退出'、'quit'、'q' 或按 Ctrl+C 结束对话")
        print("="*60)

        # 中文演示问题
        演示问题 = [
            "你好，请简单介绍一下LangGraph的核心概念",
            "LangGraph相比传统链式调用有什么优势？",
            "能否提供一个简单的LangGraph代码示例？",
            "退出"
        ]
        问题索引 = 0

        while True:
            try:
                # 获取用户输入
                print(f"\n👤 您: ", end="", flush=True)

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

                # 检查退出命令
                if 用户输入.lower() in ['退出', 'quit', 'exit', 'q']:
                    print(f"\n🤖 AI: 感谢您的使用！再见！👋")
                    break

                if not 用户输入:
                    continue

                # 显示AI正在思考
                print("🤖 AI: ", end="", flush=True)

                # 发送消息并获取回应
                回应 = await 助手.对话(用户输入)

                # 打印格式化的回应
                print(回应)

                # 短暂延迟，避免过快响应
                await asyncio.sleep(1)

            except KeyboardInterrupt:
                print(f"\n🤖 AI: 检测到中断，正在安全退出...👋")
                break
            except Exception as e:
                print(f"\n❌ 对话出错: {e}")

    except Exception as e:
        print(f"❌ 启动失败: {e}")


async def main():
    """主函数"""
    await 优化对话()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n\n👋 程序被用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常退出: {e}")
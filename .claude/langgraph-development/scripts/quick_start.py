#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph一键快速启动工具

专为初学者设计的零配置启动脚本，自动检测环境、安装依赖、
启动示例，让用户在5分钟内体验LangGraph的强大功能。
"""

import os
import sys
import json
import subprocess
import time
import webbrowser
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse

class QuickStart:
    """LangGraph快速启动器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.requirements = [
            "langgraph>=0.2.16",
            "langchain>=0.3.0",
            "langchain-openai>=0.2.0",
            "langchain-anthropic>=0.2.0",
            "langchain-community>=0.3.0",
            "python-dotenv>=1.0.0",
            "rich>=13.0.0",
            "jupyter>=1.1.0",
            "notebook>=7.0.0"
        ]
        self.min_python_version = (3, 9)

    def print_banner(self):
        """打印欢迎横幅"""
        banner = """
🚀 LangGraph 快速启动工具 v1.0

✨ 让你在5分钟内体验LangGraph的强大功能
🎯 专为初学者设计，零配置启动
📚 包含完整示例和交互式教程

        """
        print(banner)

    def check_python_version(self) -> bool:
        """检查Python版本"""
        version = sys.version_info
        if version >= self.min_python_version:
            print(f"✅ Python版本检查通过: {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
            print(f"   需要Python {'.'.join(map(str, self.min_python_version))} 或更高版本")
            return False

    def check_dependencies(self) -> List[str]:
        """检查已安装的依赖"""
        missing = []
        for package in self.requirements:
            package_name = package.split('>=')[0].split('==')[0]
            try:
                __import__(package_name.replace('-', '_'))
                print(f"✅ {package_name} 已安装")
            except ImportError:
                print(f"❌ {package_name} 未安装")
                missing.append(package)
        return missing

    def install_dependencies(self, missing_packages: List[str]) -> bool:
        """安装缺失的依赖"""
        if not missing_packages:
            return True

        print(f"\n📦 正在安装 {len(missing_packages)} 个依赖包...")
        print("   这可能需要几分钟时间，请耐心等待...")

        try:
            # 升级pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                         check=True, capture_output=True)

            # 安装依赖
            cmd = [sys.executable, "-m", "pip", "install"] + missing_packages
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)

            print("✅ 依赖安装完成!")
            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            print(f"   错误信息: {e.stderr}")
            return False

    def create_env_file(self) -> bool:
        """创建环境配置文件"""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"

        if env_file.exists():
            print("✅ 环境配置文件已存在")
            return True

        print("📝 创建环境配置文件...")

        env_content = """# LangGraph 环境配置
# 复制此文件为 .env 并填入你的API密钥

# OpenAI API密钥 (必需)
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API密钥 (可选)
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangSmith追踪 (可选，推荐用于学习)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=langgraph-quickstart

# 其他配置
LANGCHAIN_VERBOSE=false
"""

        try:
            with open(env_file, 'w', encoding='utf-8') as f:
                f.write(env_content)
            print("✅ 环境配置文件创建成功!")
            print(f"   文件位置: {env_file}")
            print("   请编辑文件并添加你的API密钥")
            return True
        except Exception as e:
            print(f"❌ 环境配置文件创建失败: {e}")
            return False

    def setup_project_structure(self) -> bool:
        """设置项目结构"""
        print("📁 设置项目结构...")

        directories = [
            "examples",
            "notebooks",
            "data",
            "logs",
            "outputs"
        ]

        for dir_name in directories:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            print(f"✅ 创建目录: {dir_name}")

        return True

    def run_basic_test(self) -> bool:
        """运行基础测试"""
        print("🧪 运行基础功能测试...")

        test_script = '''
import asyncio
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from typing import TypedDict

class State(TypedDict):
    messages: list[str]

def chatbot(state: State):
    return {"messages": [f"收到消息: {state['messages'][0]}"]}

async def test():
    try:
        graph = StateGraph(State)
        graph.add_node("chatbot", chatbot)
        graph.set_entry_point("chatbot")
        graph.set_finish_point("chatbot")

        compiled_graph = graph.compile()

        result = await compiled_graph.ainvoke({
            "messages": ["Hello LangGraph!"]
        })

        print("✅ 基础功能测试通过!")
        return True
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test())
'''

        try:
            test_file = self.project_root / "test_basic.py"
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_script)

            result = subprocess.run([sys.executable, str(test_file)],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                print("✅ " + result.stdout.split('\n')[0])
                test_file.unlink()  # 删除测试文件
                return True
            else:
                print(f"❌ 测试失败: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            print("❌ 测试超时")
            return False
        except Exception as e:
            print(f"❌ 测试运行失败: {e}")
            return False

    def create_examples(self) -> bool:
        """创建示例文件"""
        print("📚 创建学习示例...")

        examples = {
            "hello_world.py": self._get_hello_world_example(),
            "simple_chatbot.py": self._get_simple_chatbot_example(),
            "conditional_flow.py": self._get_conditional_flow_example()
        }

        examples_dir = self.project_root / "examples"

        for filename, content in examples.items():
            file_path = examples_dir / filename
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ 创建示例: {filename}")
            except Exception as e:
                print(f"❌ 创建示例失败 {filename}: {e}")
                return False

        return True

    def _get_hello_world_example(self) -> str:
        """Hello World示例"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph Hello World 示例

这是最简单的LangGraph示例，帮助你理解基本概念
"""

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, MessageGraph
from typing import TypedDict, Annotated
import operator

# 方法1: 使用StateGraph (推荐)
class State(TypedDict):
    messages: Annotated[list, operator.add]

def chatbot(state: State):
    """简单的聊天机器人函数"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 简单的回复逻辑
    if "你好" in last_message:
        response = "你好！我是LangGraph助手，很高兴认识你！"
    elif "功能" in last_message:
        response = "LangGraph是一个强大的框架，可以构建复杂的多步骤AI应用。"
    else:
        response = f"我收到你的消息: {last_message}"

    return {"messages": [AIMessage(content=response)]}

def create_state_graph():
    """创建基于StateGraph的工作流"""
    graph = StateGraph(State)

    # 添加节点
    graph.add_node("chatbot", chatbot)

    # 设置入口和出口
    graph.set_entry_point("chatbot")
    graph.set_finish_point("chatbot")

    return graph.compile()

# 方法2: 使用MessageGraph (更简单)
def message_handler(messages):
    """消息处理器"""
    last_message = messages[-1].content if messages else ""

    if "你好" in last_message:
        return AIMessage(content="你好！很高兴见到你！")
    else:
        return AIMessage(content=f"你说: {last_message}")

def create_message_graph():
    """创建基于MessageGraph的工作流"""
    graph = MessageGraph()

    graph.add_node("handler", message_handler)
    graph.set_entry_point("handler")
    graph.set_finish_point("handler")

    return graph.compile()

async def main():
    """主函数"""
    print("🚀 LangGraph Hello World 示例")
    print("=" * 50)

    # 创建并运行StateGraph示例
    print("📝 StateGraph 示例:")
    state_graph = create_state_graph()

    result1 = await state_graph.ainvoke({
        "messages": [HumanMessage(content="你好")]
    })
    print(f"输入: 你好")
    print(f"输出: {result1['messages'][-1].content}")
    print()

    result2 = await state_graph.ainvoke({
        "messages": [HumanMessage(content="LangGraph有什么功能?")]
    })
    print(f"输入: LangGraph有什么功能?")
    print(f"输出: {result2['messages'][-1].content}")
    print()

    # 创建并运行MessageGraph示例
    print("📝 MessageGraph 示例:")
    message_graph = create_message_graph()

    result3 = await message_graph.ainvoke([
        HumanMessage(content="测试消息")
    ])
    print(f"输入: 测试消息")
    print(f"输出: {result3[-1].content}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

    def _get_simple_chatbot_example(self) -> str:
        """简单聊天机器人示例"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph简单聊天机器人示例

演示如何创建一个有状态的对话系统
"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated
import operator

class State(TypedDict):
    messages: Annotated[list, operator.add]
    user_name: str

def chatbot_with_memory(state: State):
    """有记忆的聊天机器人"""
    messages = state["messages"]
    user_name = state.get("user_name", "用户")

    # 获取最后一条人类消息
    human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
    if not human_messages:
        return {"messages": [AIMessage(content="你好！我是你的AI助手。")] }

    last_message = human_messages[-1].content

    # 简单的对话逻辑
    if "我叫" in last_message:
        # 提取用户名
        name = last_message.replace("我叫", "").strip()
        return {
            "messages": [AIMessage(content=f"很高兴认识你，{name}！")],
            "user_name": name
        }
    elif user_name != "用户" and "名字" in last_message:
        return {
            "messages": [AIMessage(content=f"我记得你叫{user_name}！")]
        }
    elif "天气" in last_message:
        return {
            "messages": [AIMessage(content="今天天气晴朗，适合学习编程！")]
        }
    else:
        return {
            "messages": [AIMessage(content=f"{user_name}，你说: {last_message}")]
        }

def create_chatbot():
    """创建聊天机器人"""
    graph = StateGraph(State)

    # 添加节点
    graph.add_node("chatbot", chatbot_with_memory)

    # 设置入口和出口
    graph.set_entry_point("chatbot")
    graph.set_finish_point("chatbot")

    # 添加内存检查点，用于保存对话历史
    memory = MemorySaver()

    return graph.compile(checkpointer=memory)

async def main():
    """主函数"""
    print("🤖 LangGraph 记忆聊天机器人")
    print("=" * 50)
    print("输入消息进行对话，输入 'quit' 退出")
    print()

    chatbot = create_chatbot()

    # 初始化对话
    config = {"configurable": {"thread_id": "conversation-1"}}

    while True:
        try:
            user_input = input("你: ").strip()

            if user_input.lower() in ['quit', '退出', 'q']:
                print("👋 再见！")
                break

            if not user_input:
                continue

            # 发送消息给聊天机器人
            response = await chatbot.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config=config
            )

            # 获取AI回复
            ai_message = response["messages"][-1]
            print(f"机器人: {ai_message.content}")

        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

    def _get_conditional_flow_example(self) -> str:
        """条件流程示例"""
        return '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph条件流程示例

演示如何根据条件动态控制工作流路径
"""

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph
from typing import TypedDict, Annotated, Literal
import operator
import re

class State(TypedDict):
    messages: Annotated[list, operator.add]
    query_type: str
    confidence: float

def classify_query(state: State):
    """查询分类器"""
    messages = state["messages"]
    last_message = messages[-1].content.lower() if messages else ""

    # 简单的关键词分类
    if any(word in last_message for word in ["计算", "算", "数学", "+", "-", "*", "/"]):
        query_type = "calculation"
    elif any(word in last_message for word in ["翻译", "translate", "英语", "英文"]):
        query_type = "translation"
    elif any(word in last_message for word in ["天气", "气温", "下雨"]):
        query_type = "weather"
    else:
        query_type = "general"

    return {"query_type": query_type, "confidence": 0.8}

def calculation_handler(state: State):
    """计算处理器"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 简单的数学计算
    try:
        # 提取数字和运算符
        expression = re.findall(r'[\d+\-*/().\s]+', last_message)
        if expression:
            result = eval(expression[0])
            response = f"计算结果: {result}"
        else:
            response = "抱歉，我无法识别这个数学表达式"
    except:
        response = "抱歉，计算时出现错误"

    return {"messages": [AIMessage(content=response)]}

def translation_handler(state: State):
    """翻译处理器"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    # 模拟翻译（实际应用中会调用翻译API）
    response = f"翻译功能: '{last_message}' -> 'Translation: {last_message}'"

    return {"messages": [AIMessage(content=response)]}

def weather_handler(state: State):
    """天气处理器"""
    response = "今天北京天气晴朗，气温25°C，适合外出活动！"

    return {"messages": [AIMessage(content=response)]}

def general_handler(state: State):
    """通用处理器"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""

    response = f"我收到了你的消息: {last_message}"

    return {"messages": [AIMessage(content=response)]}

def route_query(state: State) -> Literal["calculation", "translation", "weather", "general"]:
    """路由函数 - 根据查询类型决定下一步"""
    query_type = state.get("query_type", "general")

    if query_type == "calculation":
        return "calculation"
    elif query_type == "translation":
        return "translation"
    elif query_type == "weather":
        return "weather"
    else:
        return "general"

def create_conditional_graph():
    """创建条件路由图"""
    graph = StateGraph(State)

    # 添加节点
    graph.add_node("classify", classify_query)
    graph.add_node("calculation", calculation_handler)
    graph.add_node("translation", translation_handler)
    graph.add_node("weather", weather_handler)
    graph.add_node("general", general_handler)

    # 设置入口
    graph.set_entry_point("classify")

    # 添加条件路由
    graph.add_conditional_edges(
        "classify",
        route_query,
        {
            "calculation": "calculation",
            "translation": "translation",
            "weather": "weather",
            "general": "general"
        }
    )

    # 设置出口
    graph.set_finish_point("calculation")
    graph.set_finish_point("translation")
    graph.set_finish_point("weather")
    graph.set_finish_point("general")

    return graph.compile()

async def main():
    """主函数"""
    print("🔀 LangGraph 条件流程示例")
    print("=" * 50)
    print("支持的功能:")
    print("- 数学计算 (如: 计算 2+3)")
    print("- 翻译 (如: 翻译 hello)")
    print("- 天气查询 (如: 今天天气怎么样)")
    print("- 通用对话")
    print("输入 'quit' 退出")
    print()

    graph = create_conditional_graph()

    test_queries = [
        "计算 123 + 456",
        "翻译 hello world",
        "今天天气怎么样",
        "你好，我是新用户"
    ]

    print("🧪 运行测试示例:")
    print("-" * 30)

    for query in test_queries:
        print(f"\n输入: {query}")
        print(f"路由: ", end="")

        # 运行分类器查看路由
        classify_result = await graph.ainvoke({"messages": [HumanMessage(content=query)]})
        query_type = classify_result.get("query_type", "general")
        print(query_type)

        # 获取最终回复
        final_response = classify_result["messages"][-1].content
        print(f"输出: {final_response}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
'''

    def start_interactive_mode(self):
        """启动交互模式"""
        print("\n🎉 欢迎使用LangGraph！")
        print("\n📚 推荐的学习路径:")
        print("1. 查看 examples/hello_world.py - 理解基本概念")
        print("2. 运行 examples/simple_chatbot.py - 体验有状态对话")
        print("3. 学习 examples/conditional_flow.py - 掌握条件路由")
        print("4. 打开 Jupyter Notebook 进行交互式学习")

        # 询问是否启动Jupyter
        try:
            choice = input("\n是否启动Jupyter Notebook进行交互式学习? (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是', '']:
                self.start_jupyter()
        except KeyboardInterrupt:
            print("\n👋 再见！")

    def start_jupyter(self):
        """启动Jupyter Notebook"""
        print("\n🚀 启动Jupyter Notebook...")
        try:
            # 启动Jupyter并在浏览器中打开
            subprocess.Popen([
                sys.executable, "-m", "jupyter", "notebook",
                "--notebook-dir", str(self.project_root / "notebooks"),
                "--browser", "new"
            ])
            print("✅ Jupyter Notebook已启动")
        except Exception as e:
            print(f"❌ 启动Jupyter失败: {e}")
            print("   你可以手动运行: jupyter notebook")

    def run(self, auto_start_examples: bool = False):
        """运行快速启动流程"""
        self.print_banner()

        print("🔍 正在检查你的环境...")

        # 1. 检查Python版本
        if not self.check_python_version():
            print("\n❌ 环境检查失败，请升级Python后重试")
            return False

        # 2. 检查依赖
        missing = self.check_dependencies()

        # 3. 安装缺失依赖
        if missing:
            if not self.install_dependencies(missing):
                print("\n❌ 依赖安装失败，请手动安装后重试")
                return False

        # 4. 创建环境配置文件
        if not self.create_env_file():
            print("\n❌ 环境配置失败")
            return False

        # 5. 设置项目结构
        if not self.setup_project_structure():
            print("\n❌ 项目结构设置失败")
            return False

        # 6. 运行基础测试
        if not self.run_basic_test():
            print("\n❌ 基础测试失败，请检查安装")
            return False

        # 7. 创建示例文件
        if not self.create_examples():
            print("\n❌ 示例文件创建失败")
            return False

        print("\n🎉 LangGraph环境配置完成！")
        print("\n📂 项目结构:")
        print(f"   📁 项目根目录: {self.project_root}")
        print(f"   📁 示例代码: {self.project_root / 'examples'}")
        print(f"   📁 Jupyter笔记本: {self.project_root / 'notebooks'}")
        print(f"   📄 环境配置: {self.project_root / '.env'}")

        # 8. 询问是否启动交互模式
        self.start_interactive_mode()

        return True

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangGraph快速启动工具")
    parser.add_argument("--auto", action="store_true", help="自动模式，不询问用户输入")
    parser.add_argument("--test-only", action="store_true", help="仅运行测试")

    args = parser.parse_args()

    quick_start = QuickStart()

    if args.test_only:
        success = (
            quick_start.check_python_version() and
            len(quick_start.check_dependencies()) == 0 and
            quick_start.run_basic_test()
        )
        sys.exit(0 if success else 1)
    else:
        success = quick_start.run(auto_start_examples=args.auto)
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
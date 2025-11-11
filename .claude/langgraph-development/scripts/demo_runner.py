#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph演示运行器

快速运行各种LangGraph演示示例，让初学者立即体验LangGraph的强大功能
"""

import os
import sys
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

class DemoRunner:
    """LangGraph演示运行器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.demos = self._load_demos()

    def _load_demos(self) -> Dict:
        """加载演示配置"""
        return {
            "basic": {
                "title": "🎯 基础演示",
                "description": "展示LangGraph的核心概念",
                "demos": [
                    {
                        "id": "hello_world",
                        "title": "Hello World",
                        "description": "最简单的LangGraph应用",
                        "type": "builtin",
                        "function": "demo_hello_world"
                    },
                    {
                        "id": "state_flow",
                        "title": "状态流转",
                        "description": "演示状态在工作流中的传递",
                        "type": "builtin",
                        "function": "demo_state_flow"
                    },
                    {
                        "id": "conditional_routing",
                        "title": "条件路由",
                        "description": "根据条件决定执行路径",
                        "type": "builtin",
                        "function": "demo_conditional_routing"
                    }
                ]
            },
            "advanced": {
                "title": "🚀 高级演示",
                "description": "展示复杂的应用场景",
                "demos": [
                    {
                        "id": "memory_persistence",
                        "title": "持久化内存",
                        "description": "保存和恢复对话状态",
                        "type": "builtin",
                        "function": "demo_memory_persistence"
                    },
                    {
                        "id": "tool_integration",
                        "title": "工具集成",
                        "description": "集成外部工具和API",
                        "type": "builtin",
                        "function": "demo_tool_integration"
                    },
                    {
                        "id": "error_handling",
                        "title": "错误处理",
                        "description": "优雅地处理错误和异常",
                        "type": "builtin",
                        "function": "demo_error_handling"
                    }
                ]
            }
        }

    def print_banner(self):
        """打印横幅"""
        banner = """
🎬 LangGraph 演示运行器

🎯 体验LangGraph的强大功能
🚀 从简单到复杂的演示示例
⚡ 即时运行，无需配置

        """
        print(banner)

    def display_menu(self) -> str:
        """显示主菜单"""
        print("请选择演示类别:")
        print("0. 🏠 主菜单")
        print("1. 🎯 基础演示")
        print("2. 🚀 高级演示")
        print("3. 🎲 随机演示")
        print("q. 🚪 退出")
        return input("\n请输入选择 (0-3, q): ").strip()

    def display_demo_menu(self, category: str) -> str:
        """显示演示菜单"""
        demos = self.demos[category]
        print(f"\n{demos['title']}")
        print("=" * len(demos['title']))
        print(f"{demos['description']}\n")

        for i, demo in enumerate(demos["demos"], 1):
            print(f"{i}. {demo['title']}")
            print(f"   {demo['description']}")

        print("\n0. 🔙 返回主菜单")
        return input(f"请选择演示 (0-{len(demos['demos'])}): ").strip()

    async def run_demo(self, category: str, demo_index: int):
        """运行演示"""
        demos = self.demos[category]

        if demo_index < 0 or demo_index >= len(demos["demos"]):
            print("❌ 无效的选择")
            return

        demo = demos["demos"][demo_index]
        print(f"\n🎬 演示: {demo['title']}")
        print("=" * 50)
        print(f"📝 {demo['description']}")
        print()

        try:
            # 动态调用演示函数
            demo_function = getattr(self, demo["function"])
            await demo_function()
        except AttributeError:
            print(f"❌ 演示函数不存在: {demo['function']}")
        except Exception as e:
            print(f"❌ 演示运行失败: {e}")

    async def demo_hello_world(self):
        """Hello World演示"""
        print("🎯 演示: 创建最简单的LangGraph应用")

        # 导入必要模块
        try:
            from langchain_core.messages import HumanMessage, AIMessage
            from langgraph.graph import StateGraph
            from typing import TypedDict, Annotated
            import operator
        except ImportError as e:
            print(f"❌ 导入模块失败: {e}")
            print("请确保已安装langgraph和langchain")
            return

        class State(TypedDict):
            messages: Annotated[list, operator.add]

        def simple_chatbot(state: State):
            """简单的聊天机器人"""
            messages = state["messages"]
            last_message = messages[-1].content if messages else ""

            if "你好" in last_message:
                response = "你好！我是LangGraph助手!"
            elif "功能" in last_message:
                response = "LangGraph可以构建复杂的AI工作流!"
            else:
                response = f"收到消息: {last_message}"

            return {"messages": [AIMessage(content=response)]}

        # 创建图
        print("\n📝 创建LangGraph图...")
        graph = StateGraph(State)
        graph.add_node("chatbot", simple_chatbot)
        graph.set_entry_point("chatbot")
        graph.set_finish_point("chatbot")
        compiled_graph = graph.compile()

        print("✅ 图创建完成!")

        # 运行演示
        print("\n🚀 运行演示...")
        test_inputs = [
            "你好 LangGraph!",
            "LangGraph有什么功能?",
            "演示结束"
        ]

        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n--- 示例 {i} ---")
            print(f"用户: {user_input}")

            result = await compiled_graph.ainvoke({
                "messages": [HumanMessage(content=user_input)]
            })

            ai_response = result["messages"][-1].content
            print(f"助手: {ai_response}")

            # 稍作停顿，便于观察
            await asyncio.sleep(1)

        print("\n✅ Hello World演示完成!")

    async def demo_state_flow(self):
        """状态流转演示"""
        print("🎯 演示: 状态在工作流中的传递")

        try:
            from langchain_core.messages import HumanMessage, AIMessage
            from langgraph.graph import StateGraph
            from typing import TypedDict, Annotated
            import operator
        except ImportError as e:
            print(f"❌ 导入模块失败: {e}")
            return

        class ProcessState(TypedDict):
            input_text: str
            processed_text: str
            word_count: int
            step: str

        def text_analyzer(state: ProcessState):
            """文本分析器"""
            text = state["input_text"]
            word_count = len(text.split())
            return {
                "processed_text": text.upper(),
                "word_count": word_count,
                "step": "analysis_completed"
            }

        def text_summarizer(state: ProcessState):
            """文本总结器"""
            processed = state["processed_text"]
            summary = f"文本已处理，包含{state['word_count']}个词"
            return {
                "processed_text": summary,
                "step": "summary_completed"
            }

        # 创建多步骤工作流
        print("\n📝 创建多步骤工作流...")
        graph = StateGraph(ProcessState)

        graph.add_node("analyzer", text_analyzer)
        graph.add_node("summarizer", text_summarizer)

        graph.set_entry_point("analyzer")
        graph.add_edge("analyzer", "summarizer")
        graph.set_finish_point("summarizer")

        compiled_graph = graph.compile()
        print("✅ 多步骤图创建完成!")

        # 运行演示
        print("\n🚀 运行状态流转演示...")
        test_text = "LangGraph是一个强大的AI工作流框架"

        print(f"输入文本: {test_text}")

        result = await compiled_graph.ainvoke({
            "input_text": test_text,
            "processed_text": "",
            "word_count": 0,
            "step": "start"
        })

        print(f"\n处理结果:")
        print(f"原文本: {result['input_text']}")
        print(f"处理后: {result['processed_text']}")
        print(f"词数统计: {result['word_count']}")
        print(f"处理步骤: {result['step']}")

        print("\n✅ 状态流转演示完成!")

    async def demo_conditional_routing(self):
        """条件路由演示"""
        print("🎯 演示: 根据条件决定执行路径")

        try:
            from langchain_core.messages import HumanMessage, AIMessage
            from langgraph.graph import StateGraph
            from typing import TypedDict, Annotated, Literal
            import operator
        except ImportError as e:
            print(f"❌ 导入模块失败: {e}")
            return

        class RouterState(TypedDict):
            message: str
            category: str
            response: str

        def classifier(state: RouterState):
            """消息分类器"""
            message = state["message"].lower()

            if any(word in message for word in ["计算", "算", "数学"]):
                category = "math"
            elif any(word in message for word in ["翻译", "english", "英文"]):
                category = "translation"
            else:
                category = "general"

            return {"category": category}

        def math_handler(state: RouterState):
            """数学处理器"""
            return {"response": "正在处理数学计算..."}

        def translation_handler(state: RouterState):
            """翻译处理器"""
            return {"response": "正在处理翻译请求..."}

        def general_handler(state: RouterState):
            """通用处理器"""
            return {"response": "正在处理通用请求..."}

        def route_decision(state: RouterState) -> Literal["math", "translation", "general"]:
            """路由决策函数"""
            return state["category"]

        # 创建条件路由图
        print("\n📝 创建条件路由图...")
        graph = StateGraph(RouterState)

        graph.add_node("classifier", classifier)
        graph.add_node("math_handler", math_handler)
        graph.add_node("translation_handler", translation_handler)
        graph.add_node("general_handler", general_handler)

        graph.set_entry_point("classifier")

        graph.add_conditional_edges(
            "classifier",
            route_decision,
            {
                "math": "math_handler",
                "translation": "translation_handler",
                "general": "general_handler"
            }
        )

        graph.set_finish_point("math_handler")
        graph.set_finish_point("translation_handler")
        graph.set_finish_point("general_handler")

        compiled_graph = graph.compile()
        print("✅ 条件路由图创建完成!")

        # 运行演示
        print("\n🚀 运行条件路由演示...")
        test_messages = [
            "计算 123 + 456",
            "翻译 hello world",
            "你好，这是普通消息"
        ]

        for i, message in enumerate(test_messages, 1):
            print(f"\n--- 示例 {i} ---")
            print(f"消息: {message}")

            result = await compiled_graph.ainvoke({
                "message": message,
                "category": "",
                "response": ""
            })

            print(f"分类: {result['category']}")
            print(f"响应: {result['response']}")
            await asyncio.sleep(1)

        print("\n✅ 条件路由演示完成!")

    async def demo_memory_persistence(self):
        """持久化内存演示"""
        print("🎯 演示: 保存和恢复对话状态")

        try:
            from langchain_core.messages import HumanMessage, AIMessage
            from langgraph.graph import StateGraph
            from langgraph.checkpoint.memory import MemorySaver
            from typing import TypedDict, Annotated
            import operator
        except ImportError as e:
            print(f"❌ 导入模块失败: {e}")
            return

        class ChatState(TypedDict):
            messages: Annotated[list, operator.add]
            conversation_count: int

        def memory_chatbot(state: ChatState):
            """有记忆的聊天机器人"""
            messages = state["messages"]
            count = state.get("conversation_count", 0) + 1

            human_messages = [msg for msg in messages if isinstance(msg, HumanMessage)]
            if human_messages:
                last_message = human_messages[-1].content
                response = f"这是我们的第{count}次对话。你说: {last_message}"
            else:
                response = "你好！让我们开始对话吧。"

            return {
                "messages": [AIMessage(content=response)],
                "conversation_count": count
            }

        # 创建带内存的图
        print("\n📝 创建带内存的工作流...")
        graph = StateGraph(ChatState)
        graph.add_node("chatbot", memory_chatbot)
        graph.set_entry_point("chatbot")
        graph.set_finish_point("chatbot")

        # 添加内存检查点
        memory = MemorySaver()
        compiled_graph = graph.compile(checkpointer=memory)
        print("✅ 带内存的工作流创建完成!")

        # 运行演示
        print("\n🚀 运行持久化内存演示...")
        config = {"configurable": {"thread_id": "demo-conversation"}}

        # 第一轮对话
        print("\n--- 第一轮对话 ---")
        result1 = await compiled_graph.ainvoke(
            {"messages": [HumanMessage(content="你好")], "conversation_count": 0},
            config=config
        )
        print(f"用户: 你好")
        print(f"助手: {result1['messages'][-1].content}")

        # 第二轮对话
        print("\n--- 第二轮对话 ---")
        result2 = await compiled_graph.ainvoke(
            {"messages": [HumanMessage(content="再见")]},
            config=config
        )
        print(f"用户: 再见")
        print(f"助手: {result2['messages'][-1].content}")

        print("\n✅ 持久化内存演示完成!")

    async def demo_tool_integration(self):
        """工具集成演示"""
        print("🎯 演示: 集成外部工具和API")

        try:
            from langchain_core.messages import HumanMessage, AIMessage
            from langchain_core.tools import tool
            from langgraph.graph import StateGraph
            from langgraph.prebuilt import ToolNode
            from typing import TypedDict, Annotated
            import operator
            import time
        except ImportError as e:
            print(f"❌ 导入模块失败: {e}")
            return

        # 定义工具
        @tool
        def get_current_time(query: str) -> str:
            """获取当前时间"""
            current_time = time.strftime("%Y-%m-%d %H:%M:%S")
            return f"当前时间是: {current_time}"

        @tool
        def calculator(expression: str) -> str:
            """简单计算器"""
            try:
                # 安全的数学表达式计算
                safe_expression = expression.replace('^', '**')
                result = eval(safe_expression)
                return f"计算结果: {result}"
            except:
                return "计算错误: 无效的数学表达式"

        class ToolState(TypedDict):
            messages: Annotated[list, operator.add]

        def should_use_tools(state: ToolState):
            """判断是否需要使用工具"""
            messages = state["messages"]
            last_message = messages[-1].content if messages else ""

            if any(keyword in last_message.lower() for keyword in ["时间", "几点", "time"]):
                return "tools"
            elif any(keyword in last_message.lower() for keyword in ["计算", "算", "+", "-", "*", "/"]):
                return "tools"
            else:
                return "assistant"

        def assistant(state: ToolState):
            """助手响应"""
            messages = state["messages"]
            last_message = messages[-1].content if messages else ""
            return {"messages": [AIMessage(content=f"我收到你的消息: {last_message}")]}

        # 创建带工具的图
        print("\n📝 创建带工具的工作流...")
        tools = [get_current_time, calculator]
        tool_node = ToolNode(tools)

        graph = StateGraph(ToolState)
        graph.add_node("assistant", assistant)
        graph.add_node("tools", tool_node)

        graph.set_entry_point("assistant")
        graph.add_conditional_edges("assistant", should_use_tools)
        graph.add_edge("tools", "assistant")
        graph.set_finish_point("assistant")

        compiled_graph = graph.compile()
        print("✅ 带工具的工作流创建完成!")

        # 运行演示
        print("\n🚀 运行工具集成演示...")
        test_queries = [
            "现在几点了?",
            "计算 25 * 4",
            "你好，这是普通消息"
        ]

        for i, query in enumerate(test_queries, 1):
            print(f"\n--- 示例 {i} ---")
            print(f"用户: {query}")

            result = await compiled_graph.ainvoke({
                "messages": [HumanMessage(content=query)]
            })

            ai_response = result["messages"][-1].content
            print(f"助手: {ai_response}")
            await asyncio.sleep(1)

        print("\n✅ 工具集成演示完成!")

    async def demo_error_handling(self):
        """错误处理演示"""
        print("🎯 演示: 优雅地处理错误和异常")

        try:
            from langchain_core.messages import HumanMessage, AIMessage
            from langgraph.graph import StateGraph, END
            from typing import TypedDict, Annotated, Literal
            import operator
        except ImportError as e:
            print(f"❌ 导入模块失败: {e}")
            return

        class ErrorState(TypedDict):
            messages: Annotated[list, operator.add]
            error_count: int
            processing_successful: bool

        def safe_processor(state: ErrorState):
            """安全的处理器（可能失败）"""
            messages = state["messages"]
            last_message = messages[-1].content if messages else ""

            error_count = state.get("error_count", 0)

            # 模拟处理失败的情况
            if "错误" in last_message and error_count < 2:
                return {
                    "error_count": error_count + 1,
                    "processing_successful": False,
                    "messages": [AIMessage(content="处理失败，正在重试...")]
                }
            elif "错误" in last_message and error_count >= 2:
                return {
                    "error_count": error_count,
                    "processing_successful": False,
                    "messages": [AIMessage(content="多次重试失败，放弃处理")]
                }
            else:
                return {
                    "error_count": 0,
                    "processing_successful": True,
                    "messages": [AIMessage(content=f"成功处理: {last_message}")]
                }

        def retry_logic(state: ErrorState) -> Literal["retry", "end"]:
            """重试逻辑"""
            if state.get("processing_successful", False):
                return "end"
            elif state.get("error_count", 0) < 2:
                return "retry"
            else:
                return "end"

        # 创建带错误处理的图
        print("\n📝 创建带错误处理的工作流...")
        graph = StateGraph(ErrorState)
        graph.add_node("processor", safe_processor)

        graph.set_entry_point("processor")
        graph.add_conditional_edges("processor", retry_logic)
        graph.add_edge("processor", "processor")  # 重试边
        graph.set_finish_point("processor")

        compiled_graph = graph.compile()
        print("✅ 带错误处理的工作流创建完成!")

        # 运行演示
        print("\n🚀 运行错误处理演示...")
        test_inputs = [
            "正常处理",
            "错误处理",
            "再次错误处理"
        ]

        for i, user_input in enumerate(test_inputs, 1):
            print(f"\n--- 示例 {i} ---")
            print(f"输入: {user_input}")

            result = await compiled_graph.ainvoke({
                "messages": [HumanMessage(content=user_input)],
                "error_count": 0,
                "processing_successful": False
            })

            ai_response = result["messages"][-1].content
            print(f"处理次数: {result.get('error_count', 0) + 1}")
            print(f"响应: {ai_response}")
            await asyncio.sleep(1)

        print("\n✅ 错误处理演示完成!")

    def run_random_demo(self):
        """运行随机演示"""
        import random

        all_demos = []
        for category, category_data in self.demos.items():
            for demo in category_data["demos"]:
                all_demos.append((category, demo))

        if all_demos:
            category, demo = random.choice(all_demos)
            print(f"\n🎲 随机选择: {demo['title']} ({category})")
            return asyncio.run(self.run_demo(category, category_data["demos"].index(demo)))

    async def run(self):
        """运行演示运行器"""
        self.print_banner()

        while True:
            try:
                choice = self.display_menu()

                if choice == "q":
                    print("\n👋 感谢使用LangGraph演示运行器!")
                    break
                elif choice == "0":
                    pass  # 显示主菜单
                elif choice == "1":
                    demo_choice = self.display_demo_menu("basic")
                    if demo_choice != "0":
                        await self.run_demo("basic", int(demo_choice) - 1)
                elif choice == "2":
                    demo_choice = self.display_demo_menu("advanced")
                    if demo_choice != "0":
                        await self.run_demo("advanced", int(demo_choice) - 1)
                elif choice == "3":
                    self.run_random_demo()
                else:
                    print("❌ 无效的选择，请重试")

                if choice != "q":
                    input("\n按回车键继续...")

            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    runner = DemoRunner()
    asyncio.run(runner.run())

if __name__ == "__main__":
    main()
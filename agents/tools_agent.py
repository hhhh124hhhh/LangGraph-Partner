"""
带工具调用的LangGraph智能体
演示如何为智能体添加自定义工具
"""

import re
from typing import Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolExecutor
from langchain_core.tools import tool
from utils.llm import get_llm
from tools.weather import get_weather, format_weather_response
from tools.calculator import safe_calculate, format_calculation_response

class AgentState(Dict[str, Any]):
    """智能体状态类型定义"""
    messages: list
    current_response: str = ""
    tool_calls: list = []

# 定义工具
@tool
def weather_tool(city: str) -> str:
    """查询指定城市的天气信息"""
    weather_data = get_weather(city)
    return format_weather_response(weather_data)

@tool
def calculator_tool(expression: str) -> str:
    """计算数学表达式"""
    calc_result = safe_calculate(expression)
    return format_calculation_response(calc_result)

def create_tools_agent():
    """
    创建一个带有工具调用能力的智能体

    Returns:
        可编译的智能体图
    """
    # 初始化LLM和工具
    llm = get_llm()
    tools = [weather_tool, calculator_tool]
    tool_executor = ToolExecutor(tools)

    # 定义智能体节点
    def agent_node(state: AgentState) -> AgentState:
        """代理节点：决定是否使用工具"""
        messages = state["messages"]

        # 调用LLM决定下一步动作
        response = llm.invoke(messages)
        state["messages"].append(response)

        # 检查是否有工具调用
        if hasattr(response, 'tool_calls') and response.tool_calls:
            state["tool_calls"] = response.tool_calls
        else:
            state["current_response"] = response.content

        return state

    def tool_node(state: AgentState) -> AgentState:
        """工具节点：执行工具调用"""
        tool_calls = state["tool_calls"]
        messages = state["messages"]

        # 执行每个工具调用
        for tool_call in tool_calls:
            # 执行工具
            tool_output = tool_executor.invoke(tool_call)

            # 添加工具响应消息
            tool_message = ToolMessage(
                content=str(tool_output),
                tool_call_id=tool_call["id"]
            )
            messages.append(tool_message)

        # 清空工具调用列表
        state["tool_calls"] = []
        return state

    def should_continue(state: AgentState) -> Literal["tools", "end"]:
        """决策函数：决定是否继续执行工具"""
        return "tools" if state["tool_calls"] else "end"

    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("agent", agent_node)
    workflow.add_node("tools", tool_node)

    # 设置入口点
    workflow.set_entry_point("agent")

    # 添加条件边
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )

    # 添加工具节点回到代理节点的边
    workflow.add_edge("tools", "agent")

    # 编译智能体
    return workflow.compile()

def run_tools_agent():
    """运行工具智能体示例"""
    print("=== LangGraph 工具智能体演示 ===")
    print("支持的工具：")
    print("1. 天气查询 - 输入如：'北京今天天气怎么样？'")
    print("2. 数学计算 - 输入如：'计算 25 * 4 + 10'")
    print("输入 'quit' 退出对话\n")

    # 创建智能体
    agent = create_tools_agent()

    # 初始化状态
    state = AgentState(messages=[])

    while True:
        user_input = input("\n用户: ")
        if user_input.lower() == 'quit':
            break

        # 添加用户消息到状态
        state["messages"].append(HumanMessage(content=user_input))

        # 运行智能体
        try:
            result = agent.invoke(state)

            # 显示回复
            if result.get("current_response"):
                print(f"\n助手: {result['current_response']}")

            # 更新状态
            state = result

        except Exception as e:
            print(f"\n错误: {str(e)}")
            print("请重试...")

if __name__ == "__main__":
    run_tools_agent()
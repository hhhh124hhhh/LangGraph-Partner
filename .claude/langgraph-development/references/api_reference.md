# LangGraph API参考手册

基于Context7最新调研整理的LangGraph核心API参考。

## 核心类和函数

### StateGraph

构建状态驱动的图结构，是LangGraph的核心组件。

```python
from langgraph.graph import StateGraph
from typing import TypedDict, List, Annotated

# 定义状态类型
class AgentState(TypedDict):
    messages: Annotated[List, "消息列表"]
    user_id: str
    conversation_context: str

# 创建StateGraph
workflow = StateGraph(AgentState)
```

#### 主要方法

- `add_node(name, func)`: 添加节点
- `add_edge(start, end)`: 添加边
- `add_conditional_edges(source, path, mapping)`: 添加条件边
- `set_entry_point(node)`: 设置入口节点
- `compile(checkpointer=None, interrupt_before=None, interrupt_after=None)`: 编译图

### MessageGraph

基于消息传递的图结构，适用于对话系统。

```python
from langgraph.graph import MessageGraph

# 创建MessageGraph
workflow = MessageGraph()
```

### CompiledGraph

编译后的可执行图，包含执行引擎。

```python
# 编译图
app = workflow.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human_review"],
    interrupt_after=["tool_call"]
)

# 运行图
result = await app.ainvoke(
    {"messages": [HumanMessage(content="你好")]},
    config={"configurable": {"thread_id": "conversation-1"}}
)
```

## 节点类型

### LLM节点

```python
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage

def llm_node(state: AgentState):
    llm = ChatOpenAI(model="gpt-4")
    response = llm.invoke(state["messages"])
    return {"messages": [response]}
```

### 工具节点

```python
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

# 定义工具
@tool
def search_web(query: str) -> str:
    """搜索网络信息"""
    # 实现搜索逻辑
    return f"搜索结果: {query}"

@tool
def get_weather(location: str) -> str:
    """获取天气信息"""
    # 实现天气查询逻辑
    return f"{location}的天气: 晴天，25°C"

# 创建工具节点
tools = [search_web, get_weather]
tool_node = ToolNode(tools)
```

### 条件节点

```python
def should_continue(state: AgentState) -> str:
    """决定是否继续执行"""
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"
```

## 持久化和记忆

### MemorySaver

```python
from langgraph.checkpoint.memory import MemorySaver

# 内存持久化
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
```

### Redis持久化

基于Context7调研，Redis是生产环境推荐的持久化方案。

```python
from langgraph_checkpoint_redis import RedisSaver

# Redis持久化
redis_saver = RedisSaver.from_conn_string("redis://localhost:6379/0")
app = workflow.compile(checkpointer=redis_saver)
```

### PostgreSQL持久化

```python
from langgraph_checkpoint_postgres import PostgresSaver

# PostgreSQL持久化
postgres_saver = PostgresSaver.from_conn_string(
    "postgresql://user:password@localhost/langgraph"
)
app = workflow.compile(checkpointer=postgres_saver)
```

## 配置选项

### 编译配置

```python
app = workflow.compile(
    checkpointer=MemorySaver(),          # 检查点保存器
    interrupt_before=["human_review"],   # 在指定节点前中断
    interrupt_after=["tool_call"],       # 在指定节点后中断
    debug=False,                          # 调试模式
)
```

### 运行配置

```python
config = {
    "configurable": {
        "thread_id": "conversation-1",    # 线程ID，用于状态管理
        "checkpoint_ns": "my_app",        # 检查点命名空间
    },
    "recursion_limit": 50,                # 递归限制
    "tags": ["production"],               # 标签
}
```

## 高级功能

### 人机协作

```python
from langgraph.graph import StateGraph, START, END

# 添加人工审批节点
workflow.add_node("human_review", human_review_node)
workflow.add_edge("tool_call", "human_review")
workflow.add_edge("human_review", "continue_or_end")

# 配置中断点
app = workflow.compile(
    checkpointer=MemorySaver(),
    interrupt_before=["human_review"]
)
```

### 流式执行

```python
# 流式执行
async for event in app.astream_events(
    {"messages": [HumanMessage("你好")]},
    config={"configurable": {"thread_id": "stream-1"}},
    version="v1"
):
    print(f"事件: {event}")
```

### 错误处理

```python
from langgraph.graph import StateGraph
from typing import Optional

def robust_node(state: AgentState) -> dict:
    """带错误处理的节点"""
    try:
        # 执行主要逻辑
        result = process_data(state)
        return result
    except Exception as e:
        # 记录错误并返回安全状态
        error_message = f"处理失败: {str(e)}"
        return {
            "messages": [AIMessage(content=error_message)],
            "error": True
        }

# 重试机制
def retry_wrapper(node_func, max_retries=3):
    """节点重试包装器"""
    async def wrapper(state):
        for attempt in range(max_retries):
            try:
                return await node_func(state)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                await asyncio.sleep(2 ** attempt)  # 指数退避
    return wrapper
```

## 常用模式

### ReAct模式

```python
def react_agent():
    """ReAct (Reasoning + Acting) 模式"""

    def think(state):
        """思考步骤"""
        prompt = f"""
        当前情况: {state['messages']}

        请思考下一步应该采取什么行动，格式为:
        Thought: [你的思考]
        Action: [工具名称]
        Action Input: [工具参数]
        """
        response = llm.invoke(prompt)
        return {"messages": [response]}

    def act(state):
        """行动步骤"""
        last_message = state["messages"][-1]
        # 解析工具调用并执行
        # ...

    # 构建图
    workflow = StateGraph(AgentState)
    workflow.add_node("think", think)
    workflow.add_node("act", act)
    workflow.add_edge("think", "act")
    workflow.add_edge("act", "think")
    workflow.set_entry_point("think")

    return workflow.compile()
```

### 多代理协作

基于Context7调研的多代理模式：

```python
def supervisor_pattern():
    """Supervisor模式"""

    def supervisor(state):
        """主管代理决定下一步行动"""
        agents = ["researcher", "writer", "critic"]
        # 选择下一个代理
        next_agent = select_next_agent(state, agents)
        return {"next": next_agent, "messages": state["messages"]}

    def researcher(state):
        """研究代理"""
        # 执行研究任务
        pass

    def writer(state):
        """写作代理"""
        # 执行写作任务
        pass

    def critic(state):
        """评审代理"""
        # 执行评审任务
        pass

    # 构建图
    workflow = StateGraph(SupervisorState)
    workflow.add_node("supervisor", supervisor)
    workflow.add_node("researcher", researcher)
    workflow.add_node("writer", writer)
    workflow.add_node("critic", critic)

    # 添加条件边
    workflow.add_conditional_edges(
        "supervisor",
        lambda state: state["next"],
        {
            "researcher": "researcher",
            "writer": "writer",
            "critic": "critic",
            "END": END
        }
    )

    # 所有代理完成后回到主管
    for agent in ["researcher", "writer", "critic"]:
        workflow.add_edge(agent, "supervisor")

    workflow.set_entry_point("supervisor")
    return workflow.compile()
```

## 调试和监控

### LangSmith集成

```python
import os

# 配置LangSmith
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "my-langgraph-app"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"

# 添加标签和元数据
config = {
    "tags": ["production", "v1.0"],
    "metadata": {
        "user_id": "user123",
        "session_id": "session456"
    }
}

# 运行并追踪
result = await app.ainvoke(
    input_data,
    config=config
)
```

### 自定义日志记录

```python
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def logged_node(node_func):
    """节点日志装饰器"""
    def wrapper(state):
        logger.info(f"执行节点: {node_func.__name__}")
        logger.info(f"输入状态: {state}")

        try:
            result = node_func(state)
            logger.info(f"节点结果: {result}")
            return result
        except Exception as e:
            logger.error(f"节点错误: {e}")
            raise
    return wrapper
```

## 性能优化

### 异步执行

```python
import asyncio

async def async_llm_node(state):
    """异步LLM调用"""
    llm = ChatOpenAI(model="gpt-4")
    response = await llm.ainvoke(state["messages"])
    return {"messages": [response]}

async def parallel_tools_node(state):
    """并行工具调用"""
    last_message = state["messages"][-1]
    tool_calls = getattr(last_message, "tool_calls", [])

    # 并行执行所有工具调用
    tasks = [execute_tool(tool_call) for tool_call in tool_calls]
    results = await asyncio.gather(*tasks)

    return {"messages": results}
```

### 内存优化

```python
# 配置内存限制
app = workflow.compile(
    checkpointer=MemorySaver(
        max_entries=1000,  # 最大状态条目数
        prune_interval=60  # 清理间隔（秒）
    )
)
```

## 版本兼容性

基于Context7调研的最新版本信息：

- **Python**: 3.8+
- **LangGraph**: 0.2.74, 0.4.8, 0.5.3, 0.6.0+
- **LangChain**: 0.3.0+
- **依赖管理**: 推荐使用虚拟环境

## 最佳实践

1. **状态设计**: 保持状态结构简单清晰
2. **错误处理**: 添加适当的错误处理和重试机制
3. **日志记录**: 集成LangSmith进行追踪和调试
4. **测试**: 为每个节点编写单元测试
5. **文档**: 为复杂的工作流编写详细文档
6. **版本控制**: 检查点数据也应该版本化
7. **监控**: 生产环境中集成性能监控

## 常见问题

### Q: 如何处理长时间运行的任务？
A: 使用`interrupt_before`和`interrupt_after`进行人工干预，或者实现异步任务队列。

### Q: 如何优化大型图的性能？
A: 考虑图分解、并行执行、缓存机制和分布式部署。

### Q: 如何处理状态持久化的数据隐私？
A: 使用加密的持久化存储，定期清理敏感数据。

### Q: 如何实现动态工具加载？
A: 使用工具注册表和动态图修改功能。

# LangGraph 基础概念

## 核心组件

LangGraph 是一个用于构建有状态、多参与者应用程序的库，特别适合构建AI智能体。

### 状态图
LangGraph 使用有向图来表示应用程序的状态流转：

```python
from langgraph.graph import StateGraph

workflow = StateGraph(AgentState)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)
```

### 检查点机制
检查点可以保存状态，支持暂停和恢复：

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
workflow = workflow.compile(checkpointer=checkpointer)
```

## 应用场景

1. **对话智能体**：维护对话历史和上下文
2. **多步骤任务**：复杂任务的分解和执行
3. **工具调用**：智能选择和调用外部工具
4. **记忆系统**：长期和短期记忆管理

## 优势

- ✅ 状态管理自动化
- ✅ 可视化调试
- ✅ 错误恢复
- ✅ 并行执行支持

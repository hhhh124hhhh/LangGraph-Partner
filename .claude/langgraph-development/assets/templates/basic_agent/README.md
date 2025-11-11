# 基础LangGraph代理模板

这是一个完整的LangGraph基础代理模板，展示了核心概念和最佳实践。

## 模板特性

- **StateGraph架构**: 基于状态的图结构
- **工具集成**: 包含实用的工具示例
- **记忆管理**: 支持对话状态持久化
- **错误处理**: 完善的错误处理机制
- **异步执行**: 高性能异步操作
- **调试支持**: 集成LangSmith追踪

## 快速开始

1. **复制模板**
```bash
cp -r assets/templates/basic_agent my-agent-project
cd my-agent-project
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，添加你的API密钥
```

4. **运行代理**
```bash
python src/main.py
```

## 项目结构

```
basic_agent/
├── src/
│   ├── main.py          # 主程序入口
│   ├── agent.py         # 代理核心逻辑
│   ├── tools.py         # 工具定义
│   ├── config.py        # 配置管理
│   └── utils/
│       ├── logging.py   # 日志配置
│       └── helpers.py   # 辅助函数
├── tests/
│   ├── test_agent.py    # 代理测试
│   └── test_tools.py    # 工具测试
├── config/
│   └── settings.yaml    # 配置文件
├── requirements.txt     # 依赖列表
├── .env.example         # 环境变量示例
└── README.md           # 项目文档
```

## 核心概念

### 1. 状态管理

使用TypedDict定义强类型状态：

```python
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "对话消息"]
    user_id: str
    context: Dict[str, Any]
    step_count: int
```

### 2. 图节点

每个节点都是一个函数，接收状态并返回状态更新：

```python
def llm_node(state: AgentState) -> Dict[str, Any]:
    """LLM节点：处理推理"""
    response = llm.invoke(state["messages"])
    return {"messages": [response], "step_count": state["step_count"] + 1}
```

### 3. 条件路由

根据状态决定下一步执行路径：

```python
def should_use_tools(state: AgentState) -> str:
    """决定是否使用工具"""
    last_message = state["messages"][-1]
    return "tools" if hasattr(last_message, "tool_calls") else "end"
```

### 4. 工具集成

定义和集成各种工具：

```python
@tool
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@tool
def calculator(expression: str) -> str:
    """安全计算器"""
    # 实现安全的数学计算
    pass
```

## 自定义指南

### 添加新工具

1. 在`src/tools.py`中定义工具：
```python
@tool
def my_custom_tool(param: str) -> str:
    """自定义工具描述"""
    # 实现工具逻辑
    return result
```

2. 在代理中注册工具：
```python
tools = [get_current_time, calculator, my_custom_tool]
```

### 修改状态结构

1. 更新`AgentState`定义
2. 确保所有节点正确处理新字段
3. 更新相关的测试用例

### 集成外部API

1. 添加API客户端到`src/utils/`
2. 创建相应的工具函数
3. 添加配置选项到`config/settings.yaml`
4. 实现错误处理和重试逻辑

## 测试

运行所有测试：
```bash
pytest tests/
```

运行特定测试：
```bash
pytest tests/test_agent.py -v
```

## 调试

1. **启用LangSmith追踪**
```python
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "my-agent"
```

2. **使用LangGraph Studio**
```bash
pip install langgraph-studio
langgraph-studio
```

3. **添加断点**
```python
app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["human_review"]
)
```

## 部署

### Docker部署

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ ./src/
CMD ["python", "src/main.py"]
```

### 生产环境配置

1. 使用PostgreSQL或Redis进行状态持久化
2. 配置日志收集和监控
3. 实现API限流和认证
4. 设置健康检查端点

## 常见问题

### Q: 如何处理长对话？
A: 实现消息摘要和上下文压缩机制。

### Q: 如何优化性能？
A: 使用异步操作、缓存和并行工具执行。

### Q: 如何保证安全性？
A: 输入验证、工具沙箱化和API密钥管理。

## 扩展资源

- [LangGraph官方文档](https://python.langchain.com/docs/langgraph)
- [LangSmith追踪平台](https://smith.langchain.com)
- [本技能的API参考](../../../references/api_reference.md)
- [最佳实践指南](../../../references/best_practices.md)
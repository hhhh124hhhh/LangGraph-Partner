# 多代理系统模板

基于Context7调研的企业级多代理协作系统模板，实现Supervisor、Swarm等高级协作模式。

## 模板特性

### 🏗️ 企业级架构
- **Supervisor模式**: 中央协调的专业化代理系统
- **Swarm模式**: 动态代理切换和群体智能协作
- **Hierarchical模式**: 分层管理和决策架构
- **Event-driven模式**: 事件驱动的松耦合协作

### 🚀 生产就绪特性
- **状态持久化**: Redis、PostgreSQL多数据库支持
- **错误恢复**: 完善的容错和重试机制
- **性能监控**: LangSmith + Prometheus集成
- **负载均衡**: 智能任务分配和负载分发

### 🛡️ 企业级安全
- **权限控制**: 基于角色的访问控制
- **审计日志**: 完整的操作审计追踪
- **数据加密**: 敏感信息加密存储
- **API安全**: 认证和速率限制

## 快速开始

### 1. 环境准备

```bash
# 克隆模板
git clone <this-template> my-multi-agent
cd my-multi-agent

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，添加API密钥
```

### 2. 选择架构模式

#### Supervisor模式（推荐）
```python
from templates.multi_agent.supervisor import SupervisorAgent

# 创建Supervisor代理
supervisor = SupervisorAgent(
    agents=["researcher", "writer", "reviewer"],
    coordination_model="gpt-4",
    enable_memory=True
)

# 运行任务
result = await supervisor.ainvoke({
    "task": "研究并撰写关于人工智能发展趋势的报告"
})
```

#### Swarm模式
```python
from templates.multi_agent.swarm import SwarmAgent

# 创建Swarm代理
swarm = SwarmAgent(
    agents=[
        "web_researcher",
        "data_analyst",
        "content_generator",
        "quality_checker"
    ],
    collaboration_model="gpt-4"
)

result = await swarm.ainvoke({
    "request": "分析市场数据并生成业务报告"
})
```

### 3. 运行和监控

```bash
# 启动多代理系统
python main.py --mode supervisor

# 启动监控面板
python monitoring/monitor.py

# 运行测试
python scripts/test_multi_agent.py
```

## 架构模式详解

### 1. Supervisor模式

**核心概念**: 中央协调器管理多个专业化代理

```mermaid
graph TB
    Client[客户端] --> Supervisor[Supervisor代理]
    Supervisor --> Researcher[研究代理]
    Supervisor --> Writer[写作代理]
    Supervisor --> Reviewer[评审代理]

    Researcher --> KnowledgeBase[知识库]
    Writer --> ContentDB[内容库]
    Reviewer --> QualityMetrics[质量指标]

    Supervisor --> Response[最终响应]
```

**适用场景**:
- 内容创作和分析
- 研究报告生成
- 复杂任务分解
- 质量控制流程

**优势**:
- ✅ 明确的责任分工
- ✅ 统一协调管理
- ✅ 质量保证机制
- ✅ 易于扩展新代理

### 2. Swarm模式

**核心概念**: 代理动态切换和控制交接

```mermaid
graph LR
    Request[用户请求] --> Dispatcher[分发器]
    Dispatcher --> Agent1[代理A]
    Dispatcher --> Agent2[代理B]
    Dispatcher --> Agent3[代理C]

    Agent1 -.->|完成部分| Agent2
    Agent2 -.->|需要协助| Agent3
    Agent3 --> Final[最终结果]
```

**适用场景**:
- 动态任务分配
- 协作式问题解决
- 弹性工作流
- 自适应任务路由

**优势**:
- ✅ 灵活的任务路由
- ✅ 动态负载均衡
- ✅ 故障自动恢复
- ✅ 自适应协作

### 3. Hierarchical模式

**核心概念**: 分层管理和决策架构

```mermaid
graph TB
    Top[顶层协调器] --> Level1[一级协调器1]
    Top --> Level2[一级协调器2]

    Level1 --> Worker1[工作者1]
    Level1 --> Worker2[工作者2]
    Level1 --> Worker3[工作者3]

    Level2 --> Worker4[工作者4]
    Level2 --> Worker5[工作者5]
    Level2 --> Worker6[工作者6]
```

**适用场景**:
- 大规模任务管理
- 组织架构模拟
- 多层次决策
- 复杂系统建模

## 代理类型和职责

### 🔍 研究代理 (ResearchAgent)
```python
class ResearchAgent(BaseAgent):
    """专业的研究代理"""

    def __init__(self):
        self.tools = [
            WebSearchTool(),
            DatabaseQueryTool(),
            DocumentAnalysisTool()
        ]

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行研究任务"""
        research_topic = task["topic"]

        # 多源信息收集
        web_results = await self.web_search(research_topic)
        db_results = await self.query_database(research_topic)
        doc_results = await self.analyze_documents(research_topic)

        # 综合分析
        findings = self.synthesize_findings([
            web_results, db_results, doc_results
        ])

        return {
            "agent": "researcher",
            "findings": findings,
            "sources": self.get_sources()
        }
```

### ✍️ 写作代理 (WriterAgent)
```python
class WriterAgent(BaseAgent):
    """专业的写作代理"""

    def __init__(self):
        self.writing_models = {
            "creative": "gpt-4-creative",
            "technical": "gpt-4-technical",
            "business": "gpt-4-business"
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行写作任务"""
        content_type = task.get("type", "general")
        requirements = task["requirements"]
        research_data = task.get("research_data", {})

        # 选择合适的写作模型
        model = self.writing_models.get(content_type, "gpt-4")

        # 生成内容
        content = await self.generate_content(
            requirements=requirements,
            research_data=research_data,
            model=model
        )

        # 质量检查
        quality_score = await self.assess_quality(content)

        return {
            "agent": "writer",
            "content": content,
            "quality_score": quality_score
        }
```

### 🔍 评审代理 (ReviewerAgent)
```python
class ReviewerAgent(BaseAgent):
    """专业的评审代理"""

    def __init__(self):
        self.review_criteria = {
            "accuracy": 0.3,
            "clarity": 0.25,
            "completeness": 0.25,
            "style": 0.2
        }

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行评审任务"""
        content = task["content"]
        requirements = task.get("requirements", {})

        # 多维度评审
        scores = {}
        feedback = {}

        for criterion, weight in self.review_criteria.items():
            score, comments = await self.review_dimension(
                content, criterion, requirements
            )
            scores[criterion] = score * weight
            feedback[criterion] = comments

        # 综合评分
        overall_score = sum(scores.values())

        # 生成改进建议
        improvements = await self.generate_improvements(
            content, feedback, overall_score
        )

        return {
            "agent": "reviewer",
            "overall_score": overall_score,
            "detailed_scores": scores,
            "feedback": feedback,
            "improvements": improvements,
            "approved": overall_score >= 0.8
        }
```

## 高级功能

### 1. 动态代理注册
```python
class AgentRegistry:
    """代理注册表"""

    def __init__(self):
        self.agents = {}
        self.agent_capabilities = {}

    def register_agent(self, name: str, agent: BaseAgent, capabilities: List[str]):
        """注册新代理"""
        self.agents[name] = agent
        self.agent_capabilities[name] = capabilities

    def find_suitable_agents(self, task_requirements: List[str]) -> List[str]:
        """查找合适的代理"""
        suitable_agents = []

        for name, capabilities in self.agent_capabilities.items():
            if any(req in capabilities for req in task_requirements):
                suitable_agents.append(name)

        return suitable_agents
```

### 2. 智能任务分配
```python
class TaskDistributor:
    """智能任务分发器"""

    def __init__(self):
        self.agent_loads = {}
        self.agent_performance = {}

    async def assign_task(self, task: Dict[str, Any], available_agents: List[str]) -> str:
        """智能分配任务"""
        best_agent = None
        best_score = -1

        for agent in available_agents:
            # 计算分配评分
            score = await self.calculate_assignment_score(task, agent)

            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent

    async def calculate_assignment_score(self, task: Dict[str, Any], agent: str) -> float:
        """计算代理分配评分"""
        # 负载均衡 (40%)
        load_score = 1.0 / (1.0 + self.agent_loads.get(agent, 0))

        # 历史性能 (30%)
        perf_score = self.agent_performance.get(agent, {}).get("success_rate", 0.5)

        # 能力匹配 (30%)
        capability_score = await self.match_capabilities(task, agent)

        return load_score * 0.4 + perf_score * 0.3 + capability_score * 0.3
```

### 3. 协作消息传递
```python
class AgentCommunicator:
    """代理间通信系统"""

    def __init__(self):
        self.message_bus = asyncio.Queue()
        self.agent_channels = {}

    async def send_message(self, from_agent: str, to_agent: str, message: Dict[str, Any]):
        """发送消息"""
        envelope = {
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }

        await self.message_bus.put(envelope)

    async def broadcast_message(self, from_agent: str, message: Dict[str, Any]):
        """广播消息"""
        for agent in self.agent_channels.keys():
            if agent != from_agent:
                await self.send_message(from_agent, agent, message)

    async def get_messages(self, agent: str) -> List[Dict[str, Any]]:
        """获取代理的消息"""
        messages = []

        # 从消息总线过滤相关消息
        temp_queue = asyncio.Queue()

        # 转移消息到临时队列
        while not self.message_bus.empty():
            message = await self.message_bus.get()
            if message["to"] == agent:
                messages.append(message)
            else:
                await temp_queue.put(message)

        # 将未处理的消息放回总线
        while not temp_queue.empty():
            await self.message_bus.put(await temp_queue.get())

        return messages
```

## 监控和调试

### 1. 性能监控
```python
class MultiAgentMonitor:
    """多代理系统监控"""

    def __init__(self):
        self.metrics = {
            "agent_performance": {},
            "task_completion_times": [],
            "error_rates": {},
            "resource_usage": {}
        }

    async def track_agent_performance(self, agent: str, task_start: float,
                                     success: bool):
        """跟踪代理性能"""
        completion_time = time.time() - task_start

        if agent not in self.metrics["agent_performance"]:
            self.metrics["agent_performance"][agent] = {
                "total_tasks": 0,
                "successful_tasks": 0,
                "total_time": 0
            }

        perf = self.metrics["agent_performance"][agent]
        perf["total_tasks"] += 1
        perf["total_time"] += completion_time

        if success:
            perf["successful_tasks"] += 1
```

### 2. 可视化仪表板
```python
class DashboardServer:
    """监控仪表板服务器"""

    def __init__(self, port: int = 8080):
        self.port = port
        self.app = FastAPI()
        self.setup_routes()

    def setup_routes(self):
        """设置API路由"""

        @self.app.get("/agents/status")
        async def get_agents_status():
            """获取所有代理状态"""
            return {
                "agents": await self.get_agents_status(),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/tasks/active")
        async def get_active_tasks():
            """获取活跃任务"""
            return {
                "active_tasks": await self.get_active_tasks(),
                "timestamp": datetime.now().isoformat()
            }

        @self.app.get("/metrics/performance")
        async def get_performance_metrics():
            """获取性能指标"""
            return {
                "metrics": await self.get_performance_metrics(),
                "timestamp": datetime.now().isoformat()
            }
```

## 部署配置

### Docker部署
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 环境变量
ENV PYTHONPATH=/app
ENV AGENT_MODE=supervisor

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# 暴露端口
EXPOSE 8000 8080

# 启动命令
CMD ["python", "main.py"]
```

### Kubernetes部署
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: multi-agent-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: multi-agent
  template:
    metadata:
      labels:
        app: multi-agent
    spec:
      containers:
      - name: multi-agent
        image: multi-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: REDIS_URL
          value: "redis://redis-service:6379"
        - name: POSTGRES_URL
          value: "postgresql://postgres:password@postgres-service:5432/agents"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-key
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: multi-agent-service
spec:
  selector:
    app: multi-agent
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## 故障排查

### 常见问题和解决方案

1. **代理通信失败**
   - 检查消息总线状态
   - 验证代理注册表
   - 查看网络连接

2. **性能瓶颈**
   - 监控代理负载
   - 分析任务分配算法
   - 优化代理数量

3. **内存泄漏**
   - 检查状态清理
   - 监控内存使用
   - 优化缓存策略

4. **死锁问题**
   - 分析任务依赖图
   - 检查锁的使用
   - 实现超时机制

## 扩展和定制

### 添加新代理类型
```python
class CustomAgent(BaseAgent):
    """自定义代理基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.setup_tools()

    async def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """实现具体的业务逻辑"""
        raise NotImplementedError

    def setup_tools(self):
        """设置代理工具"""
        self.tools = []
```

### 自定义协作策略
```python
class CustomCollaborationStrategy:
    """自定义协作策略"""

    def __init__(self):
        self.rules = []

    def add_rule(self, condition: Callable, action: Callable):
        """添加协作规则"""
        self.rules.append((condition, action))

    async def apply_strategy(self, agents: List[BaseAgent], task: Dict[str, Any]):
        """应用协作策略"""
        for condition, action in self.rules:
            if await condition(agents, task):
                await action(agents, task)
```

这个多代理系统模板基于Context7对最新LangGraph生态的深度调研，提供了企业级的多代理协作解决方案，支持Supervisor、Swarm等多种高级架构模式。
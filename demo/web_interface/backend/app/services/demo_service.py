"""
演示服务
处理演示场景、示例数据、对比分析等功能
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import logging

from app.models.demo import DemoScenario, ComparisonRequest, ComparisonResult
from app.core.exceptions import ValidationError, NotFoundError

logger = logging.getLogger(__name__)


class DemoService:
    """演示服务类"""

    def __init__(self):
        """初始化演示服务"""
        self.scenarios = self._load_demo_scenarios()
        self.templates = self._load_demo_templates()

    async def get_demo_scenarios(self, category: Optional[str] = None, difficulty: Optional[str] = None) -> List[DemoScenario]:
        """
        获取演示场景列表

        Args:
            category: 场景分类过滤
            difficulty: 难度过滤

        Returns:
            演示场景列表
        """
        try:
            scenarios = self.scenarios

            # 应用过滤
            if category:
                scenarios = [s for s in scenarios if s.category == category]
            if difficulty:
                scenarios = [s for s in scenarios if s.difficulty == difficulty]

            return scenarios

        except Exception as e:
            logger.error(f"获取演示场景失败: {e}")
            raise ValidationError("获取演示场景失败", {"error": str(e)})

    async def get_scenario_detail(self, scenario_id: str) -> DemoScenario:
        """
        获取场景详情

        Args:
            scenario_id: 场景ID

        Returns:
            场景详细信息
        """
        try:
            scenario = next((s for s in self.scenarios if s.scenario_id == scenario_id), None)
            if not scenario:
                raise NotFoundError("演示场景", scenario_id)

            return scenario

        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取场景详情失败: {e}")
            raise ValidationError("获取场景详情失败", {"error": str(e)})

    async def run_demo_scenario(self, scenario_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        运行演示场景

        Args:
            scenario_id: 场景ID
            params: 运行参数

        Returns:
            运行结果
        """
        try:
            scenario = await self.get_scenario_detail(scenario_id)
            run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 模拟运行过程
            result = await self._simulate_scenario_run(scenario, params or {})

            return {
                "run_id": run_id,
                "scenario_id": scenario_id,
                "scenario_name": scenario.name,
                "params": params or {},
                "result": result,
                "completed_at": datetime.now().isoformat(),
                "success": True
            }

        except Exception as e:
            logger.error(f"运行演示场景失败: {e}")
            raise ValidationError("运行演示场景失败", {"error": str(e)})

    async def analyze_comparison(self, request: ComparisonRequest) -> ComparisonResult:
        """
        进行对比分析

        Args:
            request: 对比分析请求

        Returns:
            对比分析结果
        """
        try:
            # 验证对比类型
            valid_types = ["performance", "features", "architecture", "usability"]
            if request.comparison_type not in valid_types:
                raise ValidationError(f"对比类型必须是以下之一: {valid_types}")

            comparison_id = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 执行对比分析
            result = await self._perform_comparison_analysis(request, comparison_id)

            return result

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"对比分析失败: {e}")
            raise ValidationError("对比分析失败", {"error": str(e)})

    async def get_demo_templates(self, template_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取演示模板

        Args:
            template_type: 模板类型过滤

        Returns:
            模板列表
        """
        try:
            templates = self.templates

            # 按类型过滤
            if template_type:
                templates = [t for t in templates if t.get("type") == template_type]

            return templates

        except Exception as e:
            logger.error(f"获取演示模板失败: {e}")
            raise ValidationError("获取演示模板失败", {"error": str(e)})

    async def get_demo_samples(self, category: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        获取示例数据

        Args:
            category: 数据分类
            limit: 数据数量

        Returns:
            示例数据
        """
        try:
            sample_data = self._generate_sample_data(category, limit)

            return sample_data

        except Exception as e:
            logger.error(f"获取示例数据失败: {e}")
            raise ValidationError("获取示例数据失败", {"error": str(e)})

    def _load_demo_scenarios(self) -> List[DemoScenario]:
        """加载演示场景"""
        return [
            DemoScenario(
                scenario_id="langgraph_basics",
                name="LangGraph基础入门",
                description="学习LangGraph的基本概念和用法，包括状态图、节点和边的创建",
                category="基础教程",
                difficulty="初级",
                estimated_time=30,
                prerequisites=["Python基础", "异步编程概念"],
                learning_objectives=[
                    "理解LangGraph核心概念",
                    "创建简单的状态图",
                    "实现基本的对话流程"
                ],
                steps=[
                    {
                        "step": 1,
                        "title": "环境准备",
                        "description": "安装依赖和配置环境",
                        "code": "pip install langgraph langchain-openai",
                        "expected_result": "成功安装所有依赖"
                    },
                    {
                        "step": 2,
                        "title": "创建状态定义",
                        "description": "定义对话状态结构",
                        "code": """
from typing import TypedDict
from pydantic import BaseModel

class AgentState(BaseModel):
    user_message: str
    ai_response: str = ""
    context: str = """"",
                        "expected_result": "状态类定义成功"
                    },
                    {
                        "step": 3,
                        "title": "构建状态图",
                        "description": "添加节点和边",
                        "code": """
from langgraph.graph import StateGraph, END

def create_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("respond", respond_function)
    workflow.set_entry_point("respond")
    workflow.add_edge("respond", END)
    return workflow.compile()""",
                        "expected_result": "状态图构建完成"
                    }
                ],
                example_inputs=[
                    "你好，我想了解一下LangGraph",
                    "帮我创建一个简单的对话智能体",
                    "LangGraph和普通的Chain有什么区别？"
                ],
                expected_outputs=[
                    "友好的问候和LangGraph介绍",
                    "逐步创建智能体的指导",
                    "详细的对比解释和示例"
                ]
            ),
            DemoScenario(
                scenario_id="ai_partner_system",
                name="AI Partner智能体系统",
                description="构建一个完整的AI Partner智能体，包含个性化、记忆和工具调用",
                category="综合项目",
                difficulty="中级",
                estimated_time=60,
                prerequisites=["LangGraph基础", "向量数据库概念", "API设计"],
                learning_objectives=[
                    "集成多个组件到智能体",
                    "实现个性化对话系统",
                    "添加记忆管理功能",
                    "集成工具调用能力"
                ],
                steps=[
                    {
                        "step": 1,
                        "title": "系统架构设计",
                        "description": "设计智能体整体架构",
                        "code": "# 架构设计图和组件定义",
                        "expected_result": "清晰的架构设计方案"
                    },
                    {
                        "step": 2,
                        "title": "画像系统集成",
                        "description": "添加用户和AI画像管理",
                        "code": """
class PersonaManager:
    def __init__(self):
        self.user_persona = {}
        self.ai_persona = {}

    def get_context(self):
        return self._build_context()""",
                        "expected_result": "画像系统运行正常"
                    }
                ],
                example_inputs=[
                    "记得我之前提到的项目吗？",
                    "帮我计算 2+3*4",
                    "今天北京天气怎么样？"
                ],
                expected_outputs=[
                    "个性化的记忆回应",
                    "计算结果：14",
                    "天气信息查询结果"
                ]
            )
        ]

    def _load_demo_templates(self) -> List[Dict[str, Any]]:
        """加载演示模板"""
        return [
            {
                "template_id": "basic_agent",
                "name": "基础智能体模板",
                "type": "agent",
                "description": "简单的对话智能体模板",
                "code": """
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

class AgentState(BaseModel):
    user_message: str
    ai_response: str = ""

def create_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("respond", respond_node)
    workflow.set_entry_point("respond")
    workflow.add_edge("respond", END)
    return workflow.compile()
""",
                "usage": "用于创建简单的对话智能体",
                "dependencies": ["langgraph", "pydantic"]
            },
            {
                "template_id": "memory_agent",
                "name": "带记忆的智能体模板",
                "type": "agent",
                "description": "包含对话记忆的智能体模板",
                "code": """
class MemoryAgentState(BaseModel):
    user_message: str
    ai_response: str = ""
    conversation_history: List[Dict] = []

def load_memory(state: MemoryAgentState) -> MemoryAgentState:
    state.conversation_history = get_conversation_history()
    return state""",
                "usage": "用于需要记忆能力的对话系统",
                "dependencies": ["langgraph", "pydantic", "database"]
            }
        ]

    async def _simulate_scenario_run(self, scenario: DemoScenario, params: Dict[str, Any]) -> Dict[str, Any]:
        """模拟场景运行"""
        import time
        import random

        # 模拟处理时间
        processing_time = scenario.estimated_time * (0.8 + random.random() * 0.4)
        await asyncio.sleep(0.1)  # 实际项目中这里会有真实的处理时间

        # 生成运行结果
        steps_completed = len(scenario.steps)
        total_time = processing_time
        outputs = [f"✅ {step['title']}完成" for step in scenario.steps]

        # 生成模拟的文件列表
        generated_files = [
            f"{scenario.scenario_id}_step_{i+1}.py"
            for i in range(min(steps_completed, 3))
        ]

        # 提取学习目标
        learned_concepts = scenario.learning_objectives

        return {
            "steps_completed": steps_completed,
            "total_time": total_time,
            "outputs": outputs,
            "generated_files": generated_files,
            "learned_concepts": learned_concepts,
            "success_rate": 0.95 + random.random() * 0.05
        }

    async def _perform_comparison_analysis(self, request: ComparisonRequest, comparison_id: str) -> ComparisonResult:
        """执行对比分析"""
        # 模拟分析延迟
        await asyncio.sleep(0.1)

        # 生成分析结果
        baseline_summary = self._generate_summary(request.baseline, "基准配置")
        target_summary = self._generate_summary(request.target, "目标配置")

        differences = self._analyze_differences(request.baseline, request.target)
        similarities = self._find_similarities(request.baseline, request.target)
        performance_metrics = self._calculate_performance_metrics(request.baseline, request.target)
        recommendations = self._generate_recommendations(request.baseline, request.target, request.comparison_type)
        overall_score = self._calculate_overall_score(performance_metrics)

        return ComparisonResult(
            comparison_id=comparison_id,
            timestamp=datetime.now(),
            baseline_summary=baseline_summary,
            target_summary=target_summary,
            differences=differences,
            similarities=similarities,
            performance_metrics=performance_metrics,
            recommendations=recommendations,
            overall_score=overall_score
        )

    def _generate_sample_data(self, category: Optional[str], limit: int) -> Dict[str, Any]:
        """生成示例数据"""
        if category == "conversations" or category is None:
            conversations = [
                {
                    "id": f"conv_{i}",
                    "user": f"示例用户问题 {i}",
                    "assistant": f"示例AI回答 {i}",
                    "timestamp": (datetime.now() - timedelta(minutes=i*5)).isoformat(),
                    "metadata": {"scenario": "demo", "turn": i}
                }
                for i in range(min(limit, 20))
            ]
        else:
            conversations = []

        if category == "personas" or category is None:
            personas = [
                {
                    "id": "dev_user",
                    "name": "开发者用户",
                    "role": "软件工程师",
                    "background": "5年Python开发经验",
                    "preferences": ["技术深度", "代码示例"]
                },
                {
                    "id": "ai_assistant",
                    "name": "AI助手",
                    "role": "技术助手",
                    "background": "专门帮助开发者解决问题",
                    "capabilities": ["代码生成", "问题解答", "技术指导"]
                }
            ]
        else:
            personas = []

        if category == "tools" or category is None:
            tools = [
                {
                    "name": "calculator",
                    "description": "数学计算工具",
                    "examples": ["2+3*4", "sqrt(16)", "sin(30)"]
                },
                {
                    "name": "weather",
                    "description": "天气查询工具",
                    "examples": ["北京天气", "上海明天", "广州湿度"]
                }
            ]
        else:
            tools = []

        result = {}
        if conversations:
            result["conversations"] = conversations
        if personas:
            result["personas"] = personas
        if tools:
            result["tools"] = tools

        return result

    def _generate_summary(self, config: Dict[str, Any], config_type: str) -> str:
        """生成配置摘要"""
        if config_type == "基准配置":
            return f"基于{config.get('framework', 'LangChain')}的传统实现"
        else:
            return f"基于{config.get('framework', 'LangGraph')}的新实现"

    def _analyze_differences(self, baseline: Dict[str, Any], target: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析差异"""
        return [
            {
                "aspect": "架构复杂度",
                "baseline": "中等复杂度",
                "target": "较低复杂度",
                "improvement": "状态图简化了流程管理"
            },
            {
                "aspect": "可扩展性",
                "baseline": "有限的可扩展性",
                "target": "高度可扩展",
                "improvement": "模块化的节点设计"
            }
        ]

    def _find_similarities(self, baseline: Dict[str, Any], target: Dict[str, Any]) -> List[str]:
        """找出相似点"""
        return [
            "都基于相同的LLM模型",
            "支持类似的工具集成",
            "使用相同的嵌入模型"
        ]

    def _calculate_performance_metrics(self, baseline: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, Any]:
        """计算性能指标"""
        import random

        return {
            "response_time": {
                "baseline": round(2.0 + random.random(), 1),
                "target": round(1.5 + random.random(), 1),
                "improvement": f"{20 + random.random() * 10:.1f}%"
            },
            "memory_usage": {
                "baseline": round(250 + random.random() * 20, 0),
                "target": round(180 + random.random() * 20, 0),
                "improvement": f"{25 + random.random() * 5:.1f}%"
            },
            "accuracy": {
                "baseline": round(0.82 + random.random() * 0.05, 2),
                "target": round(0.88 + random.random() * 0.05, 2),
                "improvement": f"{5 + random.random() * 3:.1f}%"
            }
        }

    def _generate_recommendations(
        self,
        baseline: Dict[str, Any],
        target: Dict[str, Any],
        comparison_type: str
    ) -> List[str]:
        """生成建议"""
        if comparison_type == "performance":
            return [
                "建议采用新的架构以获得更好的性能",
                "考虑优化资源使用效率",
                "建议进行性能基准测试"
            ]
        elif comparison_type == "features":
            return [
                "建议保留核心功能特性",
                "考虑添加用户需要的新功能",
                "确保功能的一致性和可用性"
            ]
        else:
            return [
                "建议综合考虑各方面因素",
                "平衡性能、功能和可用性",
                "根据实际需求选择最佳方案"
            ]

    def _calculate_overall_score(self, performance_metrics: Dict[str, Any]) -> float:
        """计算总体评分"""
        # 简化的评分计算
        improvements = []
        for metric, data in performance_metrics.items():
            improvement_str = data.get("improvement", "0%")
            improvement = float(improvement_str.replace("%", ""))
            improvements.append(improvement)

        if improvements:
            avg_improvement = sum(improvements) / len(improvements)
            # 将改进百分比转换为0-1的评分
            score = min(0.7 + (avg_improvement / 100) * 0.3, 1.0)
            return round(score, 2)
        else:
            return 0.8  # 默认分数


# 全局服务实例
_demo_service: Optional[DemoService] = None


def get_demo_service() -> DemoService:
    """获取演示服务实例"""
    global _demo_service
    if _demo_service is None:
        _demo_service = DemoService()
    return _demo_service
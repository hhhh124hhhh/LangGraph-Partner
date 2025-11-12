"""
演示相关API路由
提供演示场景、示例数据、对比分析等功能
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.models.response import SuccessResponse, ErrorResponse
from app.core.exceptions import ValidationError, NotFoundError
from app.core.security import rate_limit_dependency

router = APIRouter()
router_alias = APIRouter()


class DemoScenario(BaseModel):
    """演示场景模型"""
    scenario_id: str = Field(..., description="场景ID")
    name: str = Field(..., description="场景名称")
    description: str = Field(..., description="场景描述")
    category: str = Field(..., description="场景分类")
    difficulty: str = Field(..., description="难度级别")
    estimated_time: int = Field(..., description="预计时间（分钟）")
    prerequisites: List[str] = Field(default_factory=list, description="前置条件")
    learning_objectives: List[str] = Field(default_factory=list, description="学习目标")
    steps: List[Dict[str, Any]] = Field(default_factory=list, description="演示步骤")
    example_inputs: List[str] = Field(default_factory=list, description="示例输入")
    expected_outputs: List[str] = Field(default_factory=list, description="预期输出")


class ComparisonRequest(BaseModel):
    """对比分析请求"""
    baseline: Dict[str, Any] = Field(..., description="基准配置")
    target: Dict[str, Any] = Field(..., description="目标配置")
    comparison_type: str = Field(..., description="对比类型")
    metrics: List[str] = Field(default_factory=list, description="评估指标")


class ComparisonResult(BaseModel):
    """对比分析结果"""
    comparison_id: str = Field(..., description="对比ID")
    timestamp: datetime = Field(..., description="分析时间")
    baseline_summary: str = Field(..., description="基准摘要")
    target_summary: str = Field(..., description="目标摘要")
    differences: List[Dict[str, Any]] = Field(default_factory=list, description="差异分析")
    similarities: List[str] = Field(default_factory=list, description="相似点")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="性能指标")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    overall_score: float = Field(..., description="总体评分")


@router.get("/scenarios", summary="获取演示场景")
async def get_demo_scenarios(
    category: Optional[str] = Query(None, description="场景分类过滤"),
    difficulty: Optional[str] = Query(None, description="难度过滤"),
    _: None = Depends(rate_limit_dependency)
):
    """
    获取可用的演示场景列表

    Args:
        category: 场景分类过滤
        difficulty: 难度过滤

    Returns:
        演示场景列表
    """
    try:
        # TODO: 从实际的场景配置文件加载
        # 这里暂时返回模拟场景数据
        scenarios = [
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
                    {"step": 1, "title": "环境准备", "description": "安装依赖和配置环境"},
                    {"step": 2, "title": "创建状态定义", "description": "定义对话状态结构"},
                    {"step": 3, "title": "构建状态图", "description": "添加节点和边"},
                    {"step": 4, "title": "运行对话", "description": "测试和运行智能体"}
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
                    {"step": 1, "title": "系统架构设计", "description": "设计智能体整体架构"},
                    {"step": 2, "title": "画像系统集成", "description": "添加用户和AI画像管理"},
                    {"step": 3, "title": "记忆系统实现", "description": "实现对话记忆和检索"},
                    {"step": 4, "title": "工具集成", "description": "添加天气、计算器等工具"},
                    {"step": 5, "title": "API接口开发", "description": "创建RESTful API"}
                ],
                example_inputs=[
                    "记得我之前提到的项目吗？",
                    "帮我计算 2+3*4",
                    "今天北京天气怎么样？",
                    "基于我的背景，推荐一些学习资源"
                ],
                expected_outputs=[
                    "个性化的记忆回应",
                    "计算结果：14",
                    "天气信息查询结果",
                    "基于画像的个性化推荐"
                ]
            ),
            DemoScenario(
                scenario_id="rag_chatbot",
                name="RAG问答机器人",
                description="构建基于检索增强生成的问答系统",
                category="高级应用",
                difficulty="高级",
                estimated_time=90,
                prerequisites=["向量数据库", "嵌入模型", "检索算法"],
                learning_objectives=[
                    "实现文档向量化",
                    "构建语义搜索系统",
                    "集成检索到生成流程",
                    "优化检索质量"
                ],
                steps=[
                    {"step": 1, "title": "文档处理", "description": "加载和分块文档"},
                    {"step": 2, "title": "向量化", "description": "生成文档嵌入"},
                    {"step": 3, "title": "检索实现", "description": "实现相似度搜索"},
                    {"step": 4, "title": "生成集成", "description": "将检索结果集成到生成中"}
                ],
                example_inputs=[
                    "LangGraph的主要特点是什么？",
                    "如何优化向量检索的性能？",
                    "RAG系统常见的问题有哪些？"
                ],
                expected_outputs=[
                    "基于文档的准确回答",
                    "性能优化建议",
                    "常见问题和解决方案"
                ]
            )
        ]

        # 应用过滤
        if category:
            scenarios = [s for s in scenarios if s.category == category]
        if difficulty:
            scenarios = [s for s in scenarios if s.difficulty == difficulty]

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=scenarios, message="获取演示场景成功")

    except Exception as e:
        raise ValidationError("获取演示场景失败", {"error": str(e)})


@router.get("/scenarios/{scenario_id}", summary="获取场景详情")
async def get_scenario_detail(
    scenario_id: str,
    _: None = Depends(rate_limit_dependency)
):
    """
    获取指定演示场景的详细信息

    Args:
        scenario_id: 场景ID

    Returns:
        场景详细信息
    """
    try:
        # TODO: 从实际的场景配置文件加载
        # 这里暂时返回模拟详情
        if scenario_id == "langgraph_basics":
            scenario = DemoScenario(
                scenario_id=scenario_id,
                name="LangGraph基础入门",
                description="深入学习LangGraph的核心概念和实践应用",
                category="基础教程",
                difficulty="初级",
                estimated_time=30,
                prerequisites=["Python基础", "异步编程概念"],
                learning_objectives=[
                    "理解LangGraph核心概念",
                    "创建简单的状态图",
                    "实现基本的对话流程",
                    "掌握状态管理技巧"
                ],
                steps=[
                    {
                        "step": 1,
                        "title": "环境准备",
                        "description": "安装必要的依赖包",
                        "code": "pip install langgraph langchain",
                        "expected_result": "成功安装所有依赖"
                    },
                    {
                        "step": 2,
                        "title": "创建状态定义",
                        "description": "定义智能体的状态结构",
                        "code": """
from typing import TypedDict
from pydantic import BaseModel

class AgentState(BaseModel):
    user_message: str
    ai_response: str = ""
    context: str = """"",
                        "expected_result": "状态类定义成功"
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
            )
        else:
            raise NotFoundError("演示场景", scenario_id)

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=scenario, message="获取场景详情成功")

    except NotFoundError:
        raise
    except Exception as e:
        raise ValidationError("获取场景详情失败", {"error": str(e)})


@router.post("/comparison/analyze", summary="对比分析")
async def analyze_comparison(
    request: ComparisonRequest,
    _: None = Depends(rate_limit_dependency)
):
    """
    进行系统配置的对比分析

    Args:
        request: 对比分析请求

    Returns:
        对比分析结果
    """
    try:
        # 验证对比类型
        valid_types = ["performance", "features", "architecture", " usability"]
        if request.comparison_type not in valid_types:
            raise ValidationError(f"对比类型必须是以下之一: {valid_types}")

        # TODO: 实际的对比分析逻辑
        # 这里暂时返回模拟分析结果
        comparison_id = f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        result = ComparisonResult(
            comparison_id=comparison_id,
            timestamp=datetime.now(),
            baseline_summary="基于LangChain的传统实现",
            target_summary="基于LangGraph的新实现",
            differences=[
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
            ],
            similarities=[
                "都基于相同的LLM模型",
                "支持类似的工具集成",
                "使用相同的嵌入模型"
            ],
            performance_metrics={
                "response_time": {"baseline": 2.3, "target": 1.8, "improvement": "21.7%"},
                "memory_usage": {"baseline": 256, "target": 198, "improvement": "22.7%"},
                "accuracy": {"baseline": 0.85, "target": 0.89, "improvement": "4.7%"}
            },
            recommendations=[
                "建议采用LangGraph架构以获得更好的性能",
                "保持现有的工具集成策略",
                "考虑添加更多的状态监控功能"
            ],
            overall_score=0.87
        )

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=result, message="对比分析成功")

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("对比分析失败", {"error": str(e)})


@router.get("/templates", response_model=List[Dict[str, Any]], summary="获取示例模板")
async def get_demo_templates(
    type: Optional[str] = Query(None, description="模板类型"),
    _: None = Depends(rate_limit_dependency)
):
    """
    获取演示用的代码模板

    Args:
        type: 模板类型过滤

    Returns:
        代码模板列表
    """
    try:
        # TODO: 从实际的模板文件加载
        # 这里暂时返回模拟模板数据
        templates = [
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
    # 创建状态图
    workflow = StateGraph(AgentState)

    # 添加节点
    workflow.add_node("respond", respond_node)

    # 设置流程
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
    # 加载历史对话
    state.conversation_history = get_conversation_history()
    return state

def save_memory(state: MemoryAgentState) -> MemoryAgentState:
    # 保存当前对话
    save_conversation_turn(state.user_message, state.ai_response)
    return state
""",
                "usage": "用于需要记忆能力的对话系统",
                "dependencies": ["langgraph", "pydantic", "database"]
            }
        ]

        # 按类型过滤
        if type:
            templates = [t for t in templates if t["type"] == type]

        return templates

    except Exception as e:
        raise ValidationError("获取示例模板失败", {"error": str(e)})


@router.get("/samples", response_model=Dict[str, Any], summary="获取示例数据")
async def get_demo_samples(
    category: Optional[str] = Query(None, description="数据分类"),
    limit: int = Query(default=10, ge=1, le=100, description="数据数量"),
    _: None = Depends(rate_limit_dependency)
):
    """
    获取演示用的示例数据

    Args:
        category: 数据分类
        limit: 数据数量

    Returns:
        示例数据
    """
    try:
        # TODO: 从实际的数据文件加载
        # 这里暂时返回模拟示例数据
        sample_data = {
            "conversations": [
                {
                    "id": f"conv_{i}",
                    "user": f"示例用户问题 {i}",
                    "assistant": f"示例AI回答 {i}",
                    "timestamp": datetime.now().isoformat(),
                    "metadata": {"scenario": "demo", "turn": i}
                }
                for i in range(min(limit, 20))
            ],
            "personas": [
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
            ],
            "tools": [
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
        }

        # 按分类返回
        if category:
            return {category: sample_data.get(category, [])}

        return sample_data

    except Exception as e:
        raise ValidationError("获取示例数据失败", {"error": str(e)})


@router.post("/run/{scenario_id}", summary="运行演示")
async def run_demo_scenario(
    scenario_id: str,
    params: Optional[Dict[str, Any]] = None,
    _: None = Depends(rate_limit_dependency)
):
    """
    运行指定的演示场景

    Args:
        scenario_id: 场景ID
        params: 运行参数

    Returns:
        运行结果
    """
    try:
        # TODO: 实际的演示场景运行逻辑
        # 这里暂时返回模拟运行结果
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 模拟不同场景的运行结果
        if scenario_id == "langgraph_basics":
            result = {
                "steps_completed": 4,
                "total_time": 28.5,
                "outputs": [
                    "✅ 环境准备完成",
                    "✅ 状态定义成功",
                    "✅ 状态图构建完成",
                    "✅ 基础对话测试通过"
                ],
                "generated_files": ["basic_agent.py", "state_definition.py"],
                "learned_concepts": ["StateGraph", "AgentState", "Node", "Edge"]
            }
        elif scenario_id == "ai_partner_system":
            result = {
                "steps_completed": 5,
                "total_time": 67.3,
                "outputs": [
                    "✅ 系统架构设计完成",
                    "✅ 画像系统集成成功",
                    "✅ 记忆系统运行正常",
                    "✅ 工具集成测试通过",
                    "✅ API接口开发完成"
                ],
                "generated_files": [
                    "partner_agent.py",
                    "persona_manager.py",
                    "memory_manager.py",
                    "api_endpoints.py"
                ],
                "learned_concepts": [
                    "个性化对话", "记忆管理", "工具调用", "API设计"
                ]
            }
        else:
            result = {
                "steps_completed": 3,
                "total_time": 15.0,
                "outputs": ["✅ 演示运行完成"],
                "generated_files": [],
                "learned_concepts": []
            }

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data={
            "run_id": run_id,
            "scenario_id": scenario_id,
            "params": params or {},
            "result": result,
            "completed_at": datetime.now().isoformat(),
            "success": True
        }, message="运行演示成功")

    except Exception as e:
        raise ValidationError("运行演示场景失败", {"error": str(e)})


@router.get("/export/{scenario_id}", summary="导出演示包")
async def export_demo_package(
    scenario_id: str,
    format: str = Query(default="zip", regex="^(zip|tar)$", description="导出格式"),
    _: None = Depends(rate_limit_dependency)
):
    """
    导出演示场景的完整代码包

    Args:
        scenario_id: 场景ID
        format: 导出格式

    Returns:
        代码包文件
    """
    try:
        # TODO: 实际的演示包导出逻辑
        # 这里暂时返回模拟文件内容
        if format == "zip":
            # 模拟ZIP文件内容
            content = f"""Demo Package for {scenario_id}
Generated: {datetime.now().isoformat()}

Contents:
- README.md
- main.py
- requirements.txt
- config/
- examples/
"""
            filename = f"{scenario_id}_demo.zip"
            media_type = "application/zip"
        else:
            # 模拟TAR文件内容
            content = f"""Demo Package for {scenario_id}
Generated: {datetime.now().isoformat()}

Contents:
- README.md
- main.py
- requirements.txt
- config/
- examples/
"""
            filename = f"{scenario_id}_demo.tar"
            media_type = "application/x-tar"

        return StreamingResponse(
            iter([content]),
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )

    except Exception as e:
        raise ValidationError("导出演示包失败", {"error": str(e)})
@router_alias.post("/comparison/analyze")
async def analyze_comparison_alias(request: ComparisonRequest, _: None = Depends(rate_limit_dependency)):
    return await analyze_comparison(request, _)

"""
画像相关API路由
提供用户和AI画像的查询、更新、分析等功能
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse, StreamingResponse

from app.models.persona import (
    PersonaUpdateRequest, PersonaResponse, PersonaContext,
    PersonaAnalysis, PersonaComparison, PersonaTemplate,
    PersonaValidationResult, PersonaExportRequest, PersonaImportRequest
)
from app.models.response import SuccessResponse, ErrorResponse
from app.core.exceptions import ValidationError, NotFoundError
from app.core.security import InputValidator, rate_limit_dependency

router = APIRouter()


@router.get("/context", summary="获取画像上下文")
async def get_persona_context(_: None = Depends(rate_limit_dependency)):
    """
    获取当前用户和AI的画像上下文信息

    Returns:
        画像上下文信息
    """
    try:
        # TODO: 从实际的画像管理器获取上下文
        # 这里暂时返回模拟数据
        from app.models.persona import PersonaInfo

        user_persona = PersonaInfo(
            name="张三",
            role="软件工程师",
            background="有5年Python开发经验",
            communication_style="直接、技术导向",
            expertise_areas=["Python", "FastAPI", "机器学习"],
            interests=["编程", "阅读", "音乐"],
            working_style="敏捷开发"
        )

        ai_persona = PersonaInfo(
            name="AI Partner",
            role="AI开发助手",
            background="基于LangGraph的智能体系统",
            communication_style="友好、专业、耐心",
            expertise_areas=["LangGraph", "Python", "系统设计"],
            interests=["帮助开发者", "学习新技术"],
            working_style="对话式、协作式"
        )

        context = PersonaContext(
            user_persona=user_persona,
            ai_persona=ai_persona,
            shared_context="技术协作开发",
            expertise_overlap=["Python"],
            interest_overlap=["学习新技术"],
            interaction_history=[],
            compatibility_score=0.85
        )

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=context, message="获取画像上下文成功")

    except Exception as e:
        raise ValidationError("获取画像上下文失败", {"error": str(e)})


@router.post("/update", summary="更新画像")
async def update_persona(
    request: PersonaUpdateRequest,
    _: None = Depends(rate_limit_dependency)
):
    """
    更新用户或AI的画像信息

    Args:
        request: 画像更新请求

    Returns:
        更新结果
    """
    try:
        # 验证画像数据
        validated_attributes = InputValidator.validate_persona_data(request.attributes)

        # TODO: 集成实际的画像管理器
        # 这里暂时返回模拟响应
        from app.models.persona import PersonaInfo

        updated_persona = PersonaInfo(
            name=validated_attributes.get("name", ""),
            role=validated_attributes.get("role", ""),
            background=validated_attributes.get("background", ""),
            communication_style=validated_attributes.get("communication_style", ""),
            expertise_areas=validated_attributes.get("expertise_areas", []),
            interests=validated_attributes.get("interests", []),
            working_style=validated_attributes.get("working_style", ""),
            custom_attributes=validated_attributes
        )

        response = PersonaResponse(
            success=True,
            persona_type=request.persona_type,
            persona_info=updated_persona,
            message=f"{request.persona_type}画像更新成功",
            updated_fields=list(validated_attributes.keys())
        )

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=response, message="画像更新成功")

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("画像更新失败", {"error": str(e)})


@router.get("/user", summary="获取用户画像")
async def get_user_persona(
    force_reload: bool = False,
    _: None = Depends(rate_limit_dependency)
):
    """
    获取当前用户画像信息

    Args:
        force_reload: 是否强制重新加载

    Returns:
        用户画像信息
    """
    try:
        # TODO: 从实际的画像管理器获取用户画像
        # 这里暂时返回模拟数据
        user_persona = {
            "name": "张三",
            "role": "软件工程师",
            "background": "有5年Python开发经验，专注于Web后端开发",
            "communication_style": "直接、技术导向、注重效率",
            "expertise_areas": ["Python", "FastAPI", "Django", "机器学习", "系统设计"],
            "interests": ["编程", "技术阅读", "开源项目", "音乐"],
            "working_style": "敏捷开发、TDD、代码审查",
            "custom_attributes": {
                "preferred_language": "Python",
                "experience_years": 5,
                "current_project": "AI智能体系统"
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=user_persona, message="获取用户画像成功")

    except Exception as e:
        raise ValidationError("获取用户画像失败", {"error": str(e)})


@router.get("/ai", summary="获取AI画像")
async def get_ai_persona(
    force_reload: bool = False,
    _: None = Depends(rate_limit_dependency)
):
    """
    获取当前AI画像信息

    Args:
        force_reload: 是否强制重新加载

    Returns:
        AI画像信息
    """
    try:
        # TODO: 从实际的画像管理器获取AI画像
        # 这里暂时返回模拟数据
        ai_persona = {
            "name": "AI Partner",
            "role": "AI开发助手",
            "background": "基于LangGraph框架构建的智能AI助手，专门帮助开发者进行技术对话和问题解决",
            "communication_style": "友好、专业、耐心、具有教学性",
            "expertise_areas": ["LangGraph", "Python", "FastAPI", "系统设计", "AI开发", "机器学习"],
            "interests": ["帮助开发者解决问题", "学习新技术", "知识分享", "代码优化"],
            "working_style": "对话式协作、逐步引导、代码示例驱动",
            "custom_attributes": {
                "model": "glm-4.6",
                "temperature": 0.7,
                "max_tokens": 2000,
                "capabilities": ["对话", "代码生成", "问题分析", "工具调用"]
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=ai_persona, message="获取AI画像成功")

    except Exception as e:
        raise ValidationError("获取AI画像失败", {"error": str(e)})


@router.get("/analysis", summary="画像分析")
async def analyze_persona(_: None = Depends(rate_limit_dependency)):
    """
    分析当前画像的兼容性和交互模式

    Returns:
        画像分析结果
    """
    try:
        # TODO: 实际的画像分析逻辑
        # 这里暂时返回模拟数据
        analysis = PersonaAnalysis(
            user_persona_summary="技术导向的软件工程师，偏好直接高效的沟通方式",
            ai_persona_summary="专业的AI开发助手，具有教学性和耐心",
            interaction_patterns=[
                "技术问答主导的对话模式",
                "代码示例驱动的学习方式",
                "问题解决的逐步引导模式"
            ],
            recommendations=[
                "保持技术讨论的专业深度",
                "增加更多实际代码示例",
                "提供系统性的学习路径"
            ],
            potential_issues=[
                "可能过于技术化，缺乏轻松对话",
                "对非技术话题的处理能力有限"
            ],
            improvement_areas=[
                "增加更多对话灵活性",
                "提升非技术领域的知识",
                "改进对话的自然度"
            ],
            analysis_timestamp=datetime.now()
        )

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=analysis, message="画像分析成功")

    except Exception as e:
        raise ValidationError("画像分析失败", {"error": str(e)})




@router.get("/templates", response_model=List[PersonaTemplate], summary="获取画像模板")
async def get_persona_templates(
    category: Optional[str] = None,
    _: None = Depends(rate_limit_dependency)
):
    """
    获取可用的画像模板列表

    Args:
        category: 模板分类过滤

    Returns:
        画像模板列表
    """
    try:
        # TODO: 从实际的模板存储获取模板
        # 这里暂时返回模拟模板数据
        from app.models.persona import PersonaInfo

        templates = [
            PersonaTemplate(
                template_id="dev_beginner",
                name="初级开发者",
                description="适合编程初学者的画像模板",
                category="developer",
                persona_data=PersonaInfo(
                    name="初级开发者",
                    role="程序员",
                    background="刚开始学习编程",
                    communication_style="好奇、需要详细解释",
                    expertise_areas=["基础编程"],
                    interests=["学习新技术", "解决问题"]
                ),
                usage_count=15,
                is_default=True
            ),
            PersonaTemplate(
                template_id="senior_dev",
                name="高级开发者",
                description="适合经验丰富开发者的画像模板",
                category="developer",
                persona_data=PersonaInfo(
                    name="高级开发者",
                    role="软件架构师",
                    background="多年开发经验",
                    communication_style="直接、技术深度",
                    expertise_areas=["系统设计", "架构", "性能优化"],
                    interests=["技术领导", "代码审查"]
                ),
                usage_count=8
            )
        ]

        # 按分类过滤
        if category:
            templates = [t for t in templates if t.category == category]

        return templates

    except Exception as e:
        raise ValidationError("获取画像模板失败", {"error": str(e)})


@router.post("/export", summary="导出画像")
async def export_persona(
    request: PersonaExportRequest,
    _: None = Depends(rate_limit_dependency)
):
    """
    导出画像数据

    Args:
        request: 导出请求

    Returns:
        导出的画像文件
    """
    try:
        # TODO: 实际的画像导出逻辑
        # 这里暂时返回模拟数据
        from app.models.persona import PersonaInfo

        mock_persona = PersonaInfo(
            name="导出用户",
            role="开发者",
            background="测试导出功能",
            communication_style="测试用",
            expertise_areas=["测试"],
            interests=["导出功能"]
        )

        if request.export_format == "json":
            content = mock_persona.model_dump_json(indent=2, ensure_ascii=False)
            media_type = "application/json"
            filename = "persona.json"
        elif request.export_format == "yaml":
            content = f"""# Persona Export
name: {mock_persona.name}
role: {mock_persona.role}
background: {mock_persona.background}
communication_style: {mock_persona.communication_style}
"""
            media_type = "text/yaml"
            filename = "persona.yaml"
        elif request.export_format == "markdown":
            content = f"""# {mock_persona.name}

## 角色
{mock_persona.role}

## 背景
{mock_persona.background}

## 沟通风格
{mock_persona.communication_style}

## 专业领域
{', '.join(mock_persona.expertise_areas)}

## 兴趣领域
{', '.join(mock_persona.interests)}
"""
            media_type = "text/markdown"
            filename = "persona.md"
        else:
            raise ValidationError("不支持的导出格式")

        return StreamingResponse(
            iter([content]),
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError("画像导出失败", {"error": str(e)})
@router.post("/validate", summary="画像验证")
async def validate_persona(
    persona_type: str = Query(...),
    request: dict = None,
    _: None = Depends(rate_limit_dependency)
):
    try:
        required_fields = ["name", "role"]
        completeness = 0
        for f in required_fields:
            if request and request.get(f):
                completeness += 1
        score = completeness / len(required_fields)
        result = PersonaValidationResult(
            is_valid=score >= 0.5,
            completeness_score=score,
            missing_fields=[f for f in required_fields if not (request and request.get(f))],
            warnings=[]
        )
        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=result, message="画像验证成功")
    except Exception as e:
        raise ValidationError("画像验证失败", {"error": str(e)})

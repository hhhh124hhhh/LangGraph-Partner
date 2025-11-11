"""
画像服务
处理用户和AI画像的管理和分析
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import json

from app.models.persona import (
    PersonaUpdateRequest, PersonaResponse, PersonaContext,
    PersonaAnalysis, PersonaValidationResult, PersonaTemplate
)
from app.core.exceptions import ValidationError, NotFoundError
from app.core.security import InputValidator
from app.utils.ai_partner import get_ai_partner_service

logger = logging.getLogger(__name__)


class PersonaService:
    """画像服务类"""

    def __init__(self):
        """初始化画像服务"""
        self.ai_partner = get_ai_partner_service()

    async def get_persona_context(self) -> PersonaContext:
        """
        获取画像上下文信息

        Returns:
            画像上下文
        """
        try:
            # 从AI Partner获取画像上下文
            context_str = self.ai_partner.get_persona_context()

            # 解析上下文字符串，构建结构化数据
            user_persona, ai_persona = self._parse_persona_context(context_str)

            # 分析重叠领域
            expertise_overlap = list(
                set(user_persona.expertise_areas) & set(ai_persona.expertise_areas)
            )
            interest_overlap = list(
                set(user_persona.interests) & set(ai_persona.interests)
            )

            # 计算兼容性分数
            compatibility_score = self._calculate_compatibility(
                user_persona, ai_persona
            )

            context = PersonaContext(
                user_persona=user_persona,
                ai_persona=ai_persona,
                shared_context=self._extract_shared_context(context_str),
                expertise_overlap=expertise_overlap,
                interest_overlap=interest_overlap,
                interaction_history=[],  # TODO: 从记忆系统获取
                compatibility_score=compatibility_score
            )

            return context

        except Exception as e:
            logger.error(f"获取画像上下文失败: {e}")
            raise ValidationError("获取画像上下文失败", {"error": str(e)})

    async def update_persona(self, request: PersonaUpdateRequest) -> PersonaResponse:
        """
        更新画像信息

        Args:
            request: 画像更新请求

        Returns:
            更新结果
        """
        try:
            # 验证画像数据
            validated_attributes = InputValidator.validate_persona_data(request.attributes)

            # TODO: 集成实际的画像更新逻辑
            # 这里暂时模拟更新过程
            updated_fields = list(validated_attributes.keys())

            # 构建更新后的画像信息
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
                updated_fields=updated_fields
            )

            return response

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"画像更新失败: {e}")
            raise ValidationError("画像更新失败", {"error": str(e)})

    async def get_user_persona(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        获取用户画像

        Args:
            force_reload: 是否强制重新加载

        Returns:
            用户画像信息
        """
        try:
            # TODO: 从实际的画像管理器获取用户画像
            # 这里暂时返回模拟数据
            user_persona = {
                "name": "开发者用户",
                "role": "软件工程师",
                "background": "专注于AI和Web开发，有5年Python经验",
                "communication_style": "直接、技术导向、注重实践",
                "expertise_areas": ["Python", "FastAPI", "LangGraph", "机器学习", "系统设计"],
                "interests": ["新技术研究", "开源项目", "技术写作", "编程教育"],
                "working_style": "敏捷开发、TDD、代码审查",
                "custom_attributes": {
                    "preferred_language": "Python",
                    "experience_years": 5,
                    "current_focus": "AI智能体开发",
                    "learning_style": "实践导向",
                    "collaboration_preference": "技术讨论"
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            return user_persona

        except Exception as e:
            logger.error(f"获取用户画像失败: {e}")
            raise ValidationError("获取用户画像失败", {"error": str(e)})

    async def get_ai_persona(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        获取AI画像

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
                "background": "基于LangGraph构建的智能AI助手，专门帮助开发者进行技术对话和问题解决",
                "communication_style": "友好、专业、耐心、具有教学性",
                "expertise_areas": [
                    "LangGraph", "Python", "FastAPI", "系统设计",
                    "AI开发", "机器学习", "API设计", "最佳实践"
                ],
                "interests": [
                    "帮助开发者解决问题", "学习新技术", "知识分享",
                    "代码优化", "架构设计", "技术指导"
                ],
                "working_style": "对话式协作、逐步引导、代码示例驱动",
                "custom_attributes": {
                    "model": "glm-4.6",
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "capabilities": ["对话", "代码生成", "问题分析", "工具调用"],
                    "response_style": "详细解释+代码示例",
                    "knowledge_cutoff": "2024-06"
                },
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }

            return ai_persona

        except Exception as e:
            logger.error(f"获取AI画像失败: {e}")
            raise ValidationError("获取AI画像失败", {"error": str(e)})

    async def analyze_persona(self) -> PersonaAnalysis:
        """
        分析画像兼容性和交互模式

        Returns:
            画像分析结果
        """
        try:
            # 获取画像信息
            user_persona = await self.get_user_persona()
            ai_persona = await self.get_ai_persona()

            # 生成分析结果
            analysis = PersonaAnalysis(
                user_persona_summary=self._generate_persona_summary(user_persona, "user"),
                ai_persona_summary=self._generate_persona_summary(ai_persona, "ai"),
                interaction_patterns=self._analyze_interaction_patterns(user_persona, ai_persona),
                recommendations=self._generate_recommendations(user_persona, ai_persona),
                potential_issues=self._identify_potential_issues(user_persona, ai_persona),
                improvement_areas=self._suggest_improvements(user_persona, ai_persona),
                analysis_timestamp=datetime.now()
            )

            return analysis

        except Exception as e:
            logger.error(f"画像分析失败: {e}")
            raise ValidationError("画像分析失败", {"error": str(e)})

    async def validate_persona(
        self,
        persona_type: str,
        persona_data: Dict[str, Any]
    ) -> PersonaValidationResult:
        """
        验证画像数据

        Args:
            persona_type: 画像类型
            persona_data: 画像数据

        Returns:
            验证结果
        """
        try:
            if persona_type not in ["user", "ai"]:
                raise ValidationError("画像类型必须是 user 或 ai")

            # 验证画像数据
            validated_data = InputValidator.validate_persona_data(persona_data)

            # 计算完整性分数
            completeness_score = self._calculate_completeness_score(validated_data)

            # 计算一致性分数
            consistency_score = self._calculate_consistency_score(validated_data, persona_type)

            # 生成验证警告和错误
            validation_errors = []
            validation_warnings = []

            # 检查必需字段
            required_fields = ["name", "role"]
            for field in required_fields:
                if not validated_data.get(field):
                    validation_errors.append(f"缺少必需字段: {field}")

            # 检查推荐字段
            recommended_fields = ["background", "communication_style"]
            for field in recommended_fields:
                if not validated_data.get(field):
                    validation_warnings.append(f"建议填写字段: {field}")

            # 生成改进建议
            recommendations = []
            if completeness_score < 0.7:
                recommendations.append("建议完善画像信息，提高完整性")
            if consistency_score < 0.8:
                recommendations.append("建议检查画像信息的一致性")
            if not validated_data.get("expertise_areas"):
                recommendations.append("建议添加专业领域信息")
            if not validated_data.get("interests"):
                recommendations.append("建议添加兴趣领域信息")

            validation_result = PersonaValidationResult(
                is_valid=len(validation_errors) == 0,
                validation_errors=validation_errors,
                validation_warnings=validation_warnings,
                completeness_score=completeness_score,
                consistency_score=consistency_score,
                recommendations=recommendations
            )

            return validation_result

        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"画像验证失败: {e}")
            raise ValidationError("画像验证失败", {"error": str(e)})

    async def get_persona_templates(self, category: Optional[str] = None) -> List[PersonaTemplate]:
        """
        获取画像模板

        Args:
            category: 模板分类

        Returns:
            画像模板列表
        """
        try:
            # TODO: 从实际的模板存储获取模板
            # 这里暂时返回模拟模板数据
            templates = [
                PersonaTemplate(
                    template_id="dev_beginner",
                    name="初级开发者",
                    description="适合编程初学者的画像模板",
                    category="developer",
                    usage_count=25,
                    is_default=True
                ),
                PersonaTemplate(
                    template_id="senior_dev",
                    name="高级开发者",
                    description="适合经验丰富开发者的画像模板",
                    category="developer",
                    usage_count=18
                ),
                PersonaTemplate(
                    template_id="ai_researcher",
                    name="AI研究员",
                    description="适合AI研究人员的画像模板",
                    category="researcher",
                    usage_count=12
                )
            ]

            # 按分类过滤
            if category:
                templates = [t for t in templates if t.category == category]

            return templates

        except Exception as e:
            logger.error(f"获取画像模板失败: {e}")
            raise ValidationError("获取画像模板失败", {"error": str(e)})

    def _parse_persona_context(self, context_str: str) -> tuple:
        """解析画像上下文字符串"""
        # 这里简化处理，实际应该使用更复杂的解析逻辑
        from app.models.persona import PersonaInfo

        user_persona = PersonaInfo(
            name="开发者用户",
            role="软件工程师",
            background="专注于AI开发",
            communication_style="技术导向",
            expertise_areas=["Python", "LangGraph"],
            interests=["编程", "学习"]
        )

        ai_persona = PersonaInfo(
            name="AI Partner",
            role="AI助手",
            background="基于LangGraph",
            communication_style="友好专业",
            expertise_areas=["LangGraph", "Python"],
            interests=["帮助开发者"]
        )

        return user_persona, ai_persona

    def _extract_shared_context(self, context_str: str) -> str:
        """提取共享上下文"""
        return "技术协作开发，共同构建AI系统"

    def _calculate_compatibility(self, user_persona, ai_persona) -> float:
        """计算兼容性分数"""
        # 简单的兼容性计算逻辑
        expertise_overlap = len(
            set(user_persona.expertise_areas) & set(ai_persona.expertise_areas)
        )
        interest_overlap = len(
            set(user_persona.interests) & set(ai_persona.interests)
        )

        total_possible = max(
            len(user_persona.expertise_areas) + len(user_persona.interests),
            len(ai_persona.expertise_areas) + len(ai_persona.interests),
            1
        )

        compatibility = (expertise_overlap + interest_overlap) / total_possible
        return min(compatibility * 1.2, 1.0)  # 稍微提高分数

    def _generate_persona_summary(self, persona: Dict[str, Any], persona_type: str) -> str:
        """生成画像摘要"""
        if persona_type == "user":
            return f"{persona.get('role', '用户')}，{persona.get('background', '暂无背景信息')}"
        else:
            return f"{persona.get('role', 'AI助手')}，{persona.get('background', '暂无背景信息')}"

    def _analyze_interaction_patterns(self, user_persona: Dict[str, Any], ai_persona: Dict[str, Any]) -> List[str]:
        """分析交互模式"""
        patterns = []

        user_style = user_persona.get("communication_style", "").lower()
        if "技术" in user_style or "direct" in user_style:
            patterns.append("技术讨论驱动的对话模式")

        if "实践" in user_style or "example" in user_style:
            patterns.append("代码示例导向的学习方式")

        patterns.append("问题解决的逐步引导模式")
        patterns.append("知识分享和经验交流模式")

        return patterns

    def _generate_recommendations(self, user_persona: Dict[str, Any], ai_persona: Dict[str, Any]) -> List[str]:
        """生成建议"""
        recommendations = [
            "保持技术讨论的专业深度和准确性",
            "增加更多实际代码示例和最佳实践",
            "根据用户背景提供个性化的学习路径",
            "注重理论与实践相结合的解释方式"
        ]

        return recommendations

    def _identify_potential_issues(self, user_persona: Dict[str, Any], ai_persona: Dict[str, Any]) -> List[str]:
        """识别潜在问题"""
        issues = [
            "可能过于技术化，缺乏轻松对话的平衡",
            "对非技术领域话题的处理能力有限",
            "需要确保回应的一致性和准确性"
        ]

        return issues

    def _suggest_improvements(self, user_persona: Dict[str, Any], ai_persona: Dict[str, Any]) -> List[str]:
        """建议改进领域"""
        improvements = [
            "增加对话的灵活性和自然度",
            "提升非技术领域的知识和理解",
            "改进对话的个性化和适应性",
            "加强上下文理解和记忆能力"
        ]

        return improvements

    def _calculate_completeness_score(self, persona_data: Dict[str, Any]) -> float:
        """计算完整性分数"""
        important_fields = [
            "name", "role", "background", "communication_style",
            "expertise_areas", "interests", "working_style"
        ]

        filled_fields = sum(1 for field in important_fields if persona_data.get(field))
        total_fields = len(important_fields)

        return filled_fields / total_fields if total_fields > 0 else 0.0

    def _calculate_consistency_score(self, persona_data: Dict[str, Any], persona_type: str) -> float:
        """计算一致性分数"""
        # 简单的一致性检查
        score = 0.8  # 基础分数

        # 检查角色与专业领域的一致性
        role = persona_data.get("role", "").lower()
        expertise = persona_data.get("expertise_areas", [])

        if "developer" in role or "工程师" in role:
            if any("开发" in exp or "program" in exp.lower() for exp in expertise):
                score += 0.1
        elif "researcher" in role or "研究员" in role:
            if any("研究" in exp or "research" in exp.lower() for exp in expertise):
                score += 0.1

        return min(score, 1.0)


# 全局服务实例
_persona_service: Optional[PersonaService] = None


def get_persona_service() -> PersonaService:
    """获取画像服务实例"""
    global _persona_service
    if _persona_service is None:
        _persona_service = PersonaService()
    return _persona_service
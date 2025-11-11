"""
画像相关的数据模型
定义用户和AI画像的数据结构
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class PersonaAttribute(BaseModel):
    """画像属性模型"""

    key: str = Field(..., description="属性键")
    value: str = Field(..., description="属性值")
    category: Optional[str] = Field(None, description="属性分类")
    weight: float = Field(default=1.0, ge=0.0, le=1.0, description="权重")
    last_updated: datetime = Field(default_factory=datetime.now, description="最后更新时间")


class PersonaInfo(BaseModel):
    """画像信息模型"""

    name: str = Field(default="", description="姓名")
    role: str = Field(default="", description="职业角色")
    background: str = Field(default="", description="背景信息")
    communication_style: str = Field(default="", description="沟通风格")
    expertise_areas: List[str] = Field(default_factory=list, description="专业领域")
    interests: List[str] = Field(default_factory=list, description="兴趣领域")
    working_style: str = Field(default="", description="工作风格")
    custom_attributes: Dict[str, Any] = Field(default_factory=dict, description="自定义属性")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    @validator("expertise_areas", "interests")
    def validate_lists(cls, v):
        """验证列表字段"""
        if isinstance(v, str):
            # 如果是字符串，按逗号分割
            return [item.strip() for item in v.split(",") if item.strip()]
        return v


class PersonaUpdateRequest(BaseModel):
    """画像更新请求模型"""

    persona_type: str = Field(..., description="画像类型：user 或 ai")
    attributes: Dict[str, Any] = Field(..., description="要更新的属性")
    merge_strategy: str = Field(default="replace", description="合并策略：replace 或 merge")

    @validator("persona_type")
    def validate_persona_type(cls, v):
        """验证画像类型"""
        valid_types = ["user", "ai"]
        if v not in valid_types:
            raise ValueError(f"画像类型必须是以下之一: {valid_types}")
        return v

    @validator("merge_strategy")
    def validate_merge_strategy(cls, v):
        """验证合并策略"""
        valid_strategies = ["replace", "merge"]
        if v not in valid_strategies:
            raise ValueError(f"合并策略必须是以下之一: {valid_strategies}")
        return v


class PersonaResponse(BaseModel):
    """画像响应模型"""

    success: bool = Field(..., description="是否成功")
    persona_type: str = Field(..., description="画像类型")
    persona_info: PersonaInfo = Field(..., description="画像信息")
    message: str = Field(..., description="响应消息")
    updated_fields: List[str] = Field(default_factory=list, description="更新的字段列表")


class PersonaContext(BaseModel):
    """画像上下文模型"""

    user_persona: PersonaInfo = Field(..., description="用户画像")
    ai_persona: PersonaInfo = Field(..., description="AI画像")
    shared_context: str = Field(default="", description="共享上下文")
    expertise_overlap: List[str] = Field(default_factory=list, description="专业领域交集")
    interest_overlap: List[str] = Field(default_factory=list, description="兴趣领域交集")
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list, description="交互历史")
    compatibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="兼容性分数")


class PersonaAnalysis(BaseModel):
    """画像分析结果模型"""

    user_persona_summary: str = Field(..., description="用户画像摘要")
    ai_persona_summary: str = Field(..., description="AI画像摘要")
    interaction_patterns: List[str] = Field(default_factory=list, description="交互模式")
    recommendations: List[str] = Field(default_factory=list, description="建议")
    potential_issues: List[str] = Field(default_factory=list, description="潜在问题")
    improvement_areas: List[str] = Field(default_factory=list, description="改进领域")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="分析时间")


class PersonaComparison(BaseModel):
    """画像对比模型"""

    baseline_persona: PersonaInfo = Field(..., description="基准画像")
    target_persona: PersonaInfo = Field(..., description="目标画像")
    differences: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="差异分析")
    similarities: List[str] = Field(default_factory=list, description="相似点")
    compatibility_score: float = Field(default=0.0, ge=0.0, le=1.0, description="兼容性分数")
    change_summary: str = Field(default="", description="变更摘要")


class PersonaTemplate(BaseModel):
    """画像模板模型"""

    template_id: str = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    description: str = Field(..., description="模板描述")
    category: str = Field(..., description="模板分类")
    persona_data: PersonaInfo = Field(..., description="模板画像数据")
    usage_count: int = Field(default=0, description="使用次数")
    is_default: bool = Field(default=False, description="是否为默认模板")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class PersonaValidationResult(BaseModel):
    """画像验证结果模型"""

    is_valid: bool = Field(..., description="是否有效")
    validation_errors: List[str] = Field(default_factory=list, description="验证错误")
    validation_warnings: List[str] = Field(default_factory=list, description="验证警告")
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0, description="完整性分数")
    consistency_score: float = Field(default=0.0, ge=0.0, le=1.0, description="一致性分数")
    recommendations: List[str] = Field(default_factory=list, description="改进建议")


class PersonaExportRequest(BaseModel):
    """画像导出请求模型"""

    persona_type: str = Field(..., description="画像类型：user, ai 或 both")
    export_format: str = Field(default="json", description="导出格式：json, yaml, markdown")
    include_metadata: bool = Field(default=True, description="是否包含元数据")
    include_history: bool = Field(default=False, description="是否包含历史记录")

    @validator("persona_type")
    def validate_persona_type(cls, v):
        """验证画像类型"""
        valid_types = ["user", "ai", "both"]
        if v not in valid_types:
            raise ValueError(f"画像类型必须是以下之一: {valid_types}")
        return v

    @validator("export_format")
    def validate_export_format(cls, v):
        """验证导出格式"""
        valid_formats = ["json", "yaml", "markdown"]
        if v not in valid_formats:
            raise ValueError(f"导出格式必须是以下之一: {valid_formats}")
        return v


class PersonaImportRequest(BaseModel):
    """画像导入请求模型"""

    persona_data: Dict[str, Any] = Field(..., description="画像数据")
    import_strategy: str = Field(default="merge", description="导入策略：replace, merge, create_new")
    validate_before_import: bool = Field(default=True, description="导入前是否验证")
    backup_existing: bool = Field(default=True, description="是否备份现有数据")

    @validator("import_strategy")
    def validate_import_strategy(cls, v):
        """验证导入策略"""
        valid_strategies = ["replace", "merge", "create_new"]
        if v not in valid_strategies:
            raise ValueError(f"导入策略必须是以下之一: {valid_strategies}")
        return v
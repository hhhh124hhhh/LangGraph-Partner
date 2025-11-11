"""
通用响应模型
定义API响应的标准格式
"""

from typing import List, Dict, Any, Optional, Union, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, Field

T = TypeVar('T')


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模型"""

    success: bool = Field(..., description="请求是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class SuccessResponse(BaseResponse[T]):
    """成功响应模型"""

    success: bool = Field(default=True, description="请求成功")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    success: bool = Field(default=False, description="请求失败")
    error_code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")
    details: Dict[str, Any] = Field(default_factory=dict, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间戳")
    request_id: Optional[str] = Field(None, description="请求ID")
    stack_trace: Optional[str] = Field(None, description="堆栈跟踪（仅开发环境）")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""

    success: bool = Field(default=True, description="请求是否成功")
    message: str = Field(default="获取成功", description="响应消息")
    data: List[T] = Field(..., description="数据列表")
    pagination: Dict[str, Any] = Field(..., description="分页信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")


class PaginationInfo(BaseModel):
    """分页信息模型"""

    current_page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_items: int = Field(..., description="总条目数")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")
    next_page: Optional[int] = Field(None, description="下一页页码")
    prev_page: Optional[int] = Field(None, description="上一页页码")


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""

    success: bool = Field(..., description="上传是否成功")
    message: str = Field(..., description="响应消息")
    file_id: Optional[str] = Field(None, description="文件ID")
    filename: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    file_type: str = Field(..., description="文件类型")
    upload_url: Optional[str] = Field(None, description="上传URL")
    download_url: Optional[str] = Field(None, description="下载URL")
    timestamp: datetime = Field(default_factory=datetime.now, description="上传时间")


class BatchResponse(BaseModel, Generic[T]):
    """批量操作响应模型"""

    success: bool = Field(..., description="批量操作是否成功")
    message: str = Field(..., description="响应消息")
    total_count: int = Field(..., description="总数量")
    success_count: int = Field(..., description="成功数量")
    failure_count: int = Field(..., description="失败数量")
    results: List[Dict[str, Any]] = Field(..., description="操作结果列表")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")


class HealthCheckResponse(BaseModel):
    """健康检查响应模型"""

    status: str = Field(..., description="服务状态")
    timestamp: datetime = Field(..., description="检查时间")
    version: str = Field(..., description="版本号")
    services: Dict[str, str] = Field(..., description="各服务状态")
    uptime: float = Field(..., description="运行时间（秒）")
    system_info: Dict[str, Any] = Field(default_factory=dict, description="系统信息")


class StatusResponse(BaseModel):
    """状态响应模型"""

    status: str = Field(..., description="状态")
    message: str = Field(..., description="状态消息")
    details: Dict[str, Any] = Field(default_factory=dict, description="状态详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="状态时间")


class ProgressResponse(BaseModel):
    """进度响应模型"""

    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    progress: float = Field(..., ge=0.0, le=100.0, description="进度百分比")
    current_step: str = Field(..., description="当前步骤")
    total_steps: int = Field(..., description="总步骤数")
    current_step_index: int = Field(..., description="当前步骤索引")
    estimated_time_remaining: Optional[float] = Field(None, description="预计剩余时间（秒）")
    message: str = Field(..., description="状态消息")
    details: Dict[str, Any] = Field(default_factory=dict, description="详细信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")


class ValidationResponse(BaseModel):
    """验证响应模型"""

    is_valid: bool = Field(..., description="是否有效")
    message: str = Field(..., description="验证消息")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告列表")
    validation_score: float = Field(..., ge=0.0, le=1.0, description="验证分数")
    details: Dict[str, Any] = Field(default_factory=dict, description="验证详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="验证时间")


class ExportResponse(BaseModel):
    """导出响应模型"""

    success: bool = Field(..., description="导出是否成功")
    message: str = Field(..., description="响应消息")
    export_id: str = Field(..., description="导出ID")
    file_name: str = Field(..., description="导出文件名")
    file_size: int = Field(..., description="文件大小（字节）")
    download_url: str = Field(..., description="下载URL")
    expiry_time: datetime = Field(..., description="过期时间")
    format: str = Field(..., description="导出格式")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="导出时间")


class ImportResponse(BaseModel):
    """导入响应模型"""

    success: bool = Field(..., description="导入是否成功")
    message: str = Field(..., description="响应消息")
    import_id: str = Field(..., description="导入ID")
    total_records: int = Field(..., description="总记录数")
    imported_records: int = Field(..., description="成功导入记录数")
    skipped_records: int = Field(..., description="跳过记录数")
    error_records: int = Field(..., description="错误记录数")
    warnings: List[Dict[str, Any]] = Field(default_factory=list, description="警告列表")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="错误列表")
    summary: Dict[str, Any] = Field(default_factory=dict, description="导入摘要")
    timestamp: datetime = Field(default_factory=datetime.now, description="导入时间")


# 响应构建器类
class ResponseBuilder:
    """响应构建器"""

    @staticmethod
    def success(data: Any = None, message: str = "操作成功", **kwargs) -> SuccessResponse:
        """构建成功响应"""
        return SuccessResponse(
            success=True,
            message=message,
            data=data,
            **kwargs
        )

    @staticmethod
    def error(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ErrorResponse:
        """构建错误响应"""
        return ErrorResponse(
            error_code=error_code,
            message=message,
            details=details or {},
            **kwargs
        )

    @staticmethod
    def paginated(
        data: List[Any],
        total: int,
        page: int,
        page_size: int,
        message: str = "获取成功",
        **kwargs
    ) -> PaginatedResponse:
        """构建分页响应"""
        total_pages = (total + page_size - 1) // page_size
        pagination_info = PaginationInfo(
            current_page=page,
            page_size=page_size,
            total_items=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
            next_page=page + 1 if page < total_pages else None,
            prev_page=page - 1 if page > 1 else None
        )

        return PaginatedResponse(
            data=data,
            message=message,
            pagination=pagination_info.model_dump(),
            **kwargs
        )
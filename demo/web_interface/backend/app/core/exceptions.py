"""
自定义异常类
定义应用特定的异常类型和错误响应格式
"""

from typing import Dict, Any, Optional
from fastapi import HTTPException, status


class BaseAPIException(Exception):
    """API异常基类"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "error": True,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details
        }


class ValidationError(BaseAPIException):
    """数据验证错误"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(BaseAPIException):
    """资源未找到错误"""

    def __init__(self, resource: str, identifier: str = ""):
        message = f"{resource}未找到"
        if identifier:
            message += f": {identifier}"
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )


class AuthenticationError(BaseAPIException):
    """认证错误"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(BaseAPIException):
    """授权错误"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class AIServiceError(BaseAPIException):
    """AI服务错误"""

    def __init__(self, message: str, service: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="AI_SERVICE_ERROR",
            details={"service": service, **(details or {})}
        )


class MemoryError(BaseAPIException):
    """记忆系统错误"""

    def __init__(self, message: str, operation: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="MEMORY_ERROR",
            details={"operation": operation, **(details or {})}
        )


class VectorStoreError(BaseAPIException):
    """向量存储错误"""

    def __init__(self, message: str, operation: str = "unknown", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="VECTOR_STORE_ERROR",
            details={"operation": operation, **(details or {})}
        )


class SessionError(BaseAPIException):
    """会话错误"""

    def __init__(self, message: str, session_id: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="SESSION_ERROR",
            details={"session_id": session_id, **(details or {})}
        )


class ToolExecutionError(BaseAPIException):
    """工具执行错误"""

    def __init__(self, message: str, tool_name: str = "", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="TOOL_EXECUTION_ERROR",
            details={"tool_name": tool_name, **(details or {})}
        )


# 便捷的HTTP异常创建函数
def create_http_exception(exc: BaseAPIException) -> HTTPException:
    """将自定义异常转换为FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.to_dict()
    )


# 常用错误响应
COMMON_ERRORS = {
    "invalid_session": NotFoundError("会话", "无效的会话ID"),
    "ai_service_down": AIServiceError("AI服务暂时不可用"),
    "memory_corrupted": MemoryError("记忆数据损坏", "load"),
    "vector_store_unavailable": VectorStoreError("向量存储不可用", "connect"),
    "empty_message": ValidationError("消息内容不能为空"),
    "message_too_long": ValidationError("消息内容过长", {"max_length": 10000}),
    "session_expired": SessionError("会话已过期"),
}
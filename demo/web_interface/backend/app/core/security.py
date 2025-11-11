"""
安全相关功能
包括输入验证、清理和安全中间件
"""

import re
import hashlib
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator


class SecurityConfig:
    """安全配置"""

    # 输入验证限制
    MAX_MESSAGE_LENGTH = 10000
    MAX_QUERY_LENGTH = 1000
    MAX_SESSION_ID_LENGTH = 100
    MAX_USER_ID_LENGTH = 50

    # 允许的字符模式
    SAFE_MESSAGE_PATTERN = re.compile(r'^[\w\s\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf\U0002ceb0-\U0002ebef\U00030000-\U0003134f.,!?;:()[\]{}"\'-@#$%^&*+=|\\/<>`~\n\r\t]+$')
    SAFE_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    # 敏感信息模式
    SENSITIVE_PATTERNS = [
        re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),  # 信用卡号
        re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),  # 邮箱
        re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),  # IP地址
        re.compile(r'\b(?:\+?86)?1[3-9]\d{9}\b'),  # 中国手机号
    ]


class InputValidator:
    """输入验证器"""

    @staticmethod
    def sanitize_message(message: str) -> str:
        """清理和验证消息内容"""
        if not message or not message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "消息内容不能为空"}
            )

        if len(message) > SecurityConfig.MAX_MESSAGE_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": f"消息内容过长，最大允许 {SecurityConfig.MAX_MESSAGE_LENGTH} 个字符"
                }
            )

        # 检查是否包含不安全的字符
        if not SecurityConfig.SAFE_MESSAGE_PATTERN.match(message):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "消息包含不安全的字符"}
            )

        # 移除敏感信息（简单替换为占位符）
        sanitized = message
        for pattern in SecurityConfig.SENSITIVE_PATTERNS:
            sanitized = pattern.sub('[已隐藏]', sanitized)

        return sanitized.strip()

    @staticmethod
    def validate_session_id(session_id: str) -> str:
        """验证会话ID"""
        if not session_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "会话ID不能为空"}
            )

        if len(session_id) > SecurityConfig.MAX_SESSION_ID_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "会话ID过长"}
            )

        if not SecurityConfig.SAFE_ID_PATTERN.match(session_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "会话ID格式不正确"}
            )

        return session_id

    @staticmethod
    def validate_query(query: str) -> str:
        """验证搜索查询"""
        if not query or not query.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "搜索查询不能为空"}
            )

        if len(query) > SecurityConfig.MAX_QUERY_LENGTH:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "搜索查询过长"}
            )

        return query.strip()

    @staticmethod
    def validate_persona_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """验证画像数据"""
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "画像数据必须是字典格式"}
            )

        # 验证字段长度
        validated_data = {}
        for key, value in data.items():
            if isinstance(value, str) and len(value) > 1000:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={"error": f"画像字段 {key} 过长"}
                )
            validated_data[key] = value

        return validated_data


class RateLimiter:
    """简单的内存速率限制器（生产环境建议使用Redis）"""

    def __init__(self):
        self.requests = {}

    def is_allowed(self, key: str, limit: int = 60, window: int = 60) -> bool:
        """
        检查是否允许请求

        Args:
            key: 限制键（如IP地址）
            limit: 限制次数
            window: 时间窗口（秒）

        Returns:
            是否允许请求
        """
        import time

        now = time.time()
        if key not in self.requests:
            self.requests[key] = []

        # 清理过期的请求记录
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if now - req_time < window
        ]

        # 检查是否超过限制
        if len(self.requests[key]) >= limit:
            return False

        # 记录当前请求
        self.requests[key].append(now)
        return True


# 全局速率限制器实例
rate_limiter = RateLimiter()


def create_content_hash(content: str) -> str:
    """创建内容哈希"""
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def is_safe_filename(filename: str) -> bool:
    """检查文件名是否安全"""
    # 基本安全检查
    if not filename:
        return False

    # 检查危险字符
    dangerous_chars = ['..', '/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in dangerous_chars:
        if char in filename:
            return False

    # 检查扩展名
    allowed_extensions = ['.txt', '.md', '.json', '.py', '.js', '.html', '.css']
    if not any(filename.lower().endswith(ext) for ext in allowed_extensions):
        return False

    return True


# 简单的认证方案（可选实现）
class SimpleAuth(HTTPBearer):
    """简单的Bearer Token认证"""

    async def __call__(self, request: Request) -> Optional[HTTPAuthorizationCredentials]:
        credentials = await super().__call__(request)

        # 这里可以实现token验证逻辑
        # 例如：查询数据库、验证JWT等

        return credentials


# 安全中间件依赖
async def rate_limit_dependency(request: Request):
    """速率限制依赖"""
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip, limit=100, window=60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"error": "请求过于频繁，请稍后再试"}
        )
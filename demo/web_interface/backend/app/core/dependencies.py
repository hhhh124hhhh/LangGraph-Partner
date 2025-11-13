"""
依赖注入模块
提供FastAPI依赖注入功能
"""

from typing import Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .security import rate_limit_dependency


# 可选的认证依赖
async def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[str]:
    """
    可选的认证依赖
    如果提供了token则验证，否则返回None
    """
    if credentials:
        # 这里可以添加token验证逻辑
        return credentials.credentials
    return None


# 必需的认证依赖（如果需要的话）
async def require_auth(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> str:
    """
    必需的认证依赖
    要求提供有效的token
    """
    # 这里可以添加token验证逻辑
    return credentials.credentials


# 会话依赖
async def get_session_id(
    request: Request,
    auth_token: Optional[str] = Depends(optional_auth)
) -> str:
    """
    获取会话ID
    优先从header获取，其次从query参数获取，最后生成新的
    """
    # 从header获取
    session_id = request.headers.get("X-Session-ID")
    
    # 从query参数获取
    if not session_id:
        session_id = request.query_params.get("session_id")
    
    # 如果都没有，使用认证token或生成临时ID
    if not session_id:
        if auth_token:
            session_id = f"auth_{auth_token[:8]}"
        else:
            # 生成临时会话ID
            import uuid
            session_id = f"temp_{uuid.uuid4().hex[:8]}"
    
    return session_id


# 用户ID依赖
async def get_user_id(
    request: Request,
    auth_token: Optional[str] = Depends(optional_auth)
) -> Optional[str]:
    """
    获取用户ID
    从认证token中提取或返回None
    """
    if auth_token:
        # 这里可以从token中解析用户ID
        # 目前简单返回token的前8位作为用户标识
        return f"user_{auth_token[:8]}"
    
    # 从header获取用户ID（如果有的话）
    user_id = request.headers.get("X-User-ID")
    return user_id


# 安全依赖组合
async def secure_dependencies(
    request: Request,
    session_id: str = Depends(get_session_id),
    user_id: Optional[str] = Depends(get_user_id)
) -> dict:
    """
    组合多个安全依赖
    返回包含所有安全信息的字典
    """
    # 应用速率限制
    await rate_limit_dependency(request)
    
    return {
        "session_id": session_id,
        "user_id": user_id,
        "client_ip": request.client.host
    }


# 管理员权限依赖（示例）
async def require_admin(
    user_id: Optional[str] = Depends(get_user_id)
) -> str:
    """
    要求管理员权限
    """
    if not user_id or not user_id.startswith("admin_"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "需要管理员权限"}
        )
    
    return user_id
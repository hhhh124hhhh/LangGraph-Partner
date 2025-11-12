"""
FastAPI 主应用
AI Partner 智能体 API 服务
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
import json
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from app.core.config import settings
from app.core.exceptions import BaseAPIException, create_http_exception
from app.core.security import rate_limit_dependency

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s" if settings.log_format == "text" else None,
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", encoding="utf-8")
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("🚀 启动 AI Partner API 服务...")

    try:
        # 这里可以添加启动时的初始化逻辑
        # 例如：预热模型、检查数据库连接等

        logger.info("✅ 服务启动完成")
        yield

    except Exception as e:
        logger.error(f"❌ 服务启动失败: {e}")
        raise
    finally:
        # 关闭时清理
        logger.info("🔚 关闭 AI Partner API 服务...")
        # 这里可以添加清理逻辑
        logger.info("✅ 服务关闭完成")


# 创建 FastAPI 应用
app = FastAPI(
    title="AI Partner API",
    description="基于 LangGraph 的 AI 智能体对话系统 API",
    version="1.0.0",
    docs_url="/docs" if settings.api_debug else None,
    redoc_url="/redoc" if settings.api_debug else None,
    lifespan=lifespan
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加受信任主机中间件（生产环境）
if not settings.api_debug:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", settings.api_host]
    )


# 全局异常处理器
@app.exception_handler(BaseAPIException)
async def api_exception_handler(request: Request, exc: BaseAPIException):
    """处理自定义API异常"""
    logger.error(f"API异常: {exc.error_code} - {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """处理HTTP异常"""
    logger.error(f"HTTP异常: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "error_code": f"HTTP_{exc.status_code}",
            "message": exc.detail,
            "details": {}
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理异常: {type(exc).__name__} - {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误" if not settings.api_debug else str(exc),
            "details": {}
        }
    )


# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """记录请求日志"""
    import time

    start_time = time.time()

    # 记录请求信息
    logger.info(f"📥 {request.method} {request.url.path} - IP: {request.client.host}")

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        # 记录响应信息
        logger.info(f"📤 {request.method} {request.url.path} - 状态码: {response.status_code} - 耗时: {process_time:.2f}s")

        # 添加处理时间头
        response.headers["X-Process-Time"] = str(process_time)
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(f"❌ {request.method} {request.url.path} - 错误: {str(e)} - 耗时: {process_time:.2f}s")
        raise


# 根路由
@app.get("/", tags=["系统"])
async def root():
    """根路径，返回API信息"""
    return {
        "name": "AI Partner API",
        "version": "1.0.0",
        "description": "基于 LangGraph 的 AI 智能体对话系统",
        "status": "running",
        "docs_url": "/docs" if settings.api_debug else None,
        "environment": settings.get_env_info()
    }


# 健康检查
@app.get("/health", tags=["系统"])
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",  # 实际应用中应该使用当前时间
        "version": "1.0.0",
        "services": {
            "api": "healthy",
            "ai_model": "checking...",
            "vector_store": "checking...",
            "memory": "checking..."
        }
    }

@app.get("/api/health", tags=["系统"])
async def health_check_api():
    return await health_check()


# API 路由注册
def register_routers():
    """注册所有API路由"""
    from app.api import chat, persona, memory, knowledge, demo

    # 注册路由模块
    app.include_router(
        chat.router,
        prefix="/api/chat",
        tags=["对话"]
    )

    app.include_router(
        persona.router,
        prefix="/api/persona",
        tags=["画像"]
    )

    app.include_router(
        memory.router,
        prefix="/api/memory",
        tags=["记忆"]
    )

    app.include_router(
        knowledge.router,
        prefix="/api/knowledge",
        tags=["知识"]
    )

    app.include_router(
        demo.router,
        prefix="/api/demo",
        tags=["演示"]
    )

    from app.api.demo import router_alias as demo_alias
    app.include_router(
        demo_alias,
        prefix="/api",
        tags=["演示"]
    )

    logger.info("✅ 所有API路由注册完成")


# 注册路由
register_routers()


# 开发服务器启动
if __name__ == "__main__":
    logger.info("🚀 启动开发服务器...")
    logger.info(f"📍 服务地址: {settings.get_api_url()}")
    logger.info(f"📚 API文档: {settings.get_api_url()}/docs")

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("🔌 WebSocket 连接已建立")
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                if msg_type == "ping":
                    await websocket.send_json({
                        "type": "ping",
                        "payload": {},
                        "timestamp": datetime.now().isoformat()
                    })
                elif msg_type in ("subscribe", "unsubscribe"):
                    await websocket.send_json({
                        "type": "message_update",
                        "payload": {"status": "ok"},
                        "timestamp": datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"WebSocket 消息处理失败: {e}")
                await websocket.send_json({
                    "type": "error",
                    "payload": {"error": "invalid_message"},
                    "timestamp": datetime.now().isoformat()
                })
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket 连接已关闭")

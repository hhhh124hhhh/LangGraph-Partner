"""
聊天相关API路由
集成AI Partner智能体服务
"""

from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, Dict, Any
import time
import uuid
from datetime import datetime

from app.models.chat import (
    ChatRequest, ChatResponse, ChatState,
    ChatHistoryResponse, ConversationTurn,
    SearchRequest, SearchResult, ToolExecutionRequest,
    ToolExecutionResponse, SessionInfo
)
from app.models.response import ResponseBuilder
from app.core.dependencies import rate_limit_dependency
from app.core.exceptions import (
    ValidationError, AIServiceError, SessionError,
    ToolExecutionError
)
from app.core.security import InputValidator

# 导入AI Partner服务
from app.utils.ai_partner import get_ai_partner_service
# 导入会话持久化模块
from app.utils.session_persistence import (
    create_session, save_message, get_session_info, get_session_messages,
    delete_session as delete_session_data, list_all_sessions
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", summary="AI对话")
async def chat(
    request: ChatRequest,
    _: None = Depends(rate_limit_dependency)
):
    """
    与AI Partner进行对话

    Args:
        request: 对话请求

    Returns:
        AI回应结果
    """
    try:
        start_time = time.time()
        
        # 验证输入
        validated_message = InputValidator.validate_message(request.message)
        validated_session_id = InputValidator.validate_session_id(request.session_id)

        # 确保会话存在
        if not get_session_info(validated_session_id):
            create_session(validated_session_id)

        # 保存用户消息
        save_message(
            session_id=validated_session_id,
            role="user",
            content=validated_message
        )

        # 尝试使用真实的AI Partner服务
        ai_service = get_ai_partner_service()
        
        if ai_service and ai_service.is_available():
            # 使用真实的AI Partner服务
            try:
                result = await ai_service.chat(
                    message=validated_message,
                    session_id=validated_session_id
                )
                
                ai_response = result.get("response", "")
                metadata = result.get("metadata", {})
                
                processing_time = time.time() - start_time
                
                # 保存AI响应
                save_message(
                    session_id=validated_session_id,
                    role="assistant",
                    content=ai_response,
                    metadata=metadata
                )
                
                response = ChatResponse(
                    session_id=validated_session_id,
                    ai_response=ai_response,
                    processing_time=processing_time,
                    timestamp=datetime.now(),
                    metadata=metadata
                )
                
                return ResponseBuilder.success(data=response, message="对话成功")
                
            except Exception as ai_error:
                print(f"AI服务调用失败，回退到模拟响应: {ai_error}")
                # 回退到模拟响应
        
        # 模拟响应（作为后备方案）
        processing_time = time.time() - start_time
        
        # 简单的模拟回应逻辑
        mock_response = f"我收到了您的消息：{validated_message}"
        
        if "LangGraph" in validated_message:
            mock_response += "\n\nLangGraph是一个强大的框架，特别适合构建复杂的AI智能体。"
        if "帮助" in validated_message or "问题" in validated_message:
            mock_response += "\n\n我很乐意帮助您解决问题。请告诉我更多详细信息。"

        # 保存AI响应
        save_message(
            session_id=validated_session_id,
            role="assistant",
            content=mock_response,
            metadata={"service_type": "mock"}
        )

        response = ChatResponse(
            session_id=validated_session_id,
            ai_response=mock_response,
            processing_time=processing_time,
            timestamp=datetime.now(),
            metadata={"service_type": "mock"}
        )

        return ResponseBuilder.success(data=response, message="对话成功")

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise AIServiceError("对话处理失败", "ai_partner", {"error": str(e)})


@router.get("/state/{session_id}", summary="获取会话状态")
async def get_chat_state(
    session_id: str,
    _: None = Depends(rate_limit_dependency)
):
    """
    获取指定会话的状态信息

    Args:
        session_id: 会话ID

    Returns:
        会话状态信息
    """
    try:
        # 验证会话ID
        validated_session_id = InputValidator.validate_session_id(session_id)

        # 获取会话信息
        session_info = get_session_info(validated_session_id)
        
        if not session_info:
            raise SessionError("会话不存在", validated_session_id)

        # 获取会话消息数量
        messages = get_session_messages(validated_session_id, limit=1000)
        total_conversations = len([msg for msg in messages if msg["role"] == "user"])

        # 尝试使用真实的AI Partner服务获取额外信息
        ai_service = get_ai_partner_service()
        persona_active = True
        vector_store_connected = False
        memory_connected = False
        active_tools = []

        if ai_service and ai_service.is_available():
            try:
                ai_session_info = ai_service.get_session_info(validated_session_id)
                persona_active = ai_session_info.get("persona_active", True)
                vector_store_connected = ai_session_info.get("vector_store_connected", False)
                memory_connected = ai_session_info.get("memory_connected", False)
                active_tools = ai_session_info.get("active_tools", [])
            except Exception as ai_error:
                print(f"获取AI服务会话信息失败: {ai_error}")

        state = ChatState(
            session_id=validated_session_id,
            current_turn=total_conversations,
            context_summary=session_info.get("context_summary", ""),
            persona_active=persona_active,
            vector_store_connected=vector_store_connected,
            memory_connected=memory_connected,
            last_activity=session_info.get("last_activity", datetime.now()),
            active_tools=active_tools
        )

        return ResponseBuilder.success(data=state, message="获取会话状态成功")

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise SessionError("获取会话状态失败", validated_session_id, {"error": str(e)})


@router.get("/history", summary="获取对话历史")
async def get_chat_history(
    session_id: str = Query(...),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_metadata: bool = Query(True),
    _: None = Depends(rate_limit_dependency)
):
    """
    获取对话历史记录

    Args:
        session_id: 会话ID
        limit: 返回记录数量限制
        offset: 偏移量
        include_metadata: 是否包含元数据

    Returns:
        对话历史记录
    """
    try:
        # 验证会话ID
        validated_session_id = InputValidator.validate_session_id(session_id)

        # 检查会话是否存在
        session_info = get_session_info(validated_session_id)
        if not session_info:
            raise SessionError("会话不存在", validated_session_id)

        # 获取会话消息
        messages = get_session_messages(
            validated_session_id, 
            limit=limit + offset,  # 获取更多消息以支持分页
            include_metadata=include_metadata
        )

        # 应用分页
        paginated_messages = messages[offset:offset + limit]

        # 转换为ConversationTurn格式
        turns = []
        user_message = None
        ai_response = None
        
        for i, msg in enumerate(paginated_messages):
            if msg["role"] == "user":
                user_message = msg
                # 查找对应的AI响应
                if i + 1 < len(paginated_messages) and paginated_messages[i + 1]["role"] == "assistant":
                    ai_response = paginated_messages[i + 1]
                    
                    turn = ConversationTurn(
                        turn_id=f"turn_{len(turns)}",
                        session_id=validated_session_id,
                        timestamp=user_message.get("timestamp", datetime.now()),
                        user_message=user_message.get("content", ""),
                        ai_response=ai_response.get("content", ""),
                        context_used=ai_response.get("metadata", {}).get("context_used", []),
                        tools_called=ai_response.get("metadata", {}).get("tools_called", []),
                        search_query=ai_response.get("metadata", {}).get("search_query", ""),
                        retrieval_count=ai_response.get("metadata", {}).get("retrieval_count", 0),
                        metadata=ai_response.get("metadata", {}) if include_metadata else {}
                    )
                    turns.append(turn)
                    
                    user_message = None
                    ai_response = None

        # 计算总轮数（基于用户消息数量）
        all_messages = get_session_messages(validated_session_id, limit=10000)
        total_turns = len([msg for msg in all_messages if msg["role"] == "user"])

        response = ChatHistoryResponse(
            session_id=validated_session_id,
            total_turns=total_turns,
            turns=turns,
            has_more=offset + limit < total_turns,
            next_offset=offset + limit if offset + limit < total_turns else None
        )

        return ResponseBuilder.success(data=response, message="获取对话历史成功")

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise SessionError("获取对话历史失败", session_id, {"error": str(e)})


@router.post("/search", summary="语义搜索")
async def search_knowledge(
    request: SearchRequest,
    _: None = Depends(rate_limit_dependency)
):
    """
    在知识库中进行语义搜索

    Args:
        request: 搜索请求

    Returns:
        搜索结果列表
    """
    try:
        # 验证搜索查询
        validated_query = InputValidator.validate_query(request.query)

        # 尝试使用真实的AI Partner服务
        ai_service = get_ai_partner_service()
        
        if ai_service and ai_service.is_available():
            try:
                search_results = ai_service.search_knowledge(
                    query=validated_query,
                    top_k=request.top_k,
                    min_score=request.min_score
                )
                
                # 转换为SearchResult格式
                results = []
                for item in search_results:
                    result = SearchResult(
                        content=item.get("content", ""),
                        metadata=item.get("metadata", {}),
                        similarity=item.get("similarity", 0.0),
                        distance=item.get("distance", 1.0),
                        chunk_id=item.get("chunk_id", "")
                    )
                    results.append(result)
                
                return ResponseBuilder.success(data=results, message="搜索成功")
                
            except Exception as ai_error:
                print(f"知识搜索失败，使用模拟结果: {ai_error}")
                # 回退到模拟响应

        # 模拟搜索结果（作为后备方案）
        mock_results = [
            SearchResult(
                content=f"搜索结果内容 {i}: 关于{validated_query}的相关信息",
                metadata={
                    "source": "document.pdf",
                    "page": i + 1,
                    "chunk_id": f"chunk_{i}"
                },
                similarity=0.9 - (i * 0.1),
                distance=0.1 + (i * 0.1),
                chunk_id=f"chunk_{i}"
            )
            for i in range(min(request.top_k, 5))
        ]

        # 过滤相似度
        filtered_results = [
            result for result in mock_results
            if result.similarity >= request.min_score
        ]

        return ResponseBuilder.success(data=filtered_results, message="搜索成功")

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise AIServiceError("搜索失败", "vector_store", {"error": str(e)})


@router.post("/tools/execute", summary="执行工具")
async def execute_tool(
    request: ToolExecutionRequest,
    _: None = Depends(rate_limit_dependency)
):
    """
    执行指定的工具

    Args:
        request: 工具执行请求

    Returns:
        工具执行结果
    """
    try:
        start_time = time.time()

        # TODO: 集成实际的工具执行系统
        # 这里暂时返回模拟结果
        if request.tool_name == "calculator":
            result = {"calculation": f"计算结果: {request.parameters}"}
        elif request.tool_name == "weather":
            result = {"weather": f"天气信息: {request.parameters}"}
        else:
            raise ToolExecutionError(f"未知的工具: {request.tool_name}", request.tool_name)

        execution_time = time.time() - start_time

        response = ToolExecutionResponse(
            tool_name=request.tool_name,
            success=True,
            result=result,
            execution_time=execution_time,
            metadata={
                "parameters": request.parameters,
                "session_id": request.session_id
            }
        )

        return ResponseBuilder.success(data=response, message="工具执行成功")

    except ToolExecutionError:
        raise
    except Exception as e:
        raise ToolExecutionError("工具执行失败", request.tool_name, {"error": str(e)})


@router.post("/sessions", summary="创建新会话")
async def create_new_session(
    _: None = Depends(rate_limit_dependency)
):
    """
    创建新的会话

    Returns:
        新创建的会话信息
    """
    try:
        # 生成新的会话ID
        session_id = str(uuid.uuid4())
        
        # 创建会话
        create_session(session_id)
        
        session_info = get_session_info(session_id)
        
        response = SessionInfo(
            session_id=session_id,
            start_time=session_info.get("created_at", datetime.now()),
            last_update=session_info.get("last_activity", datetime.now()),
            total_turns=0,
            duration_minutes=0,
            is_active=True
        )

        return ResponseBuilder.success(data=response, message="会话创建成功")

    except Exception as e:
        raise SessionError("创建会话失败", "", {"error": str(e)})


@router.delete("/sessions/{session_id}", summary="删除会话")
async def delete_session(
    session_id: str,
    _: None = Depends(rate_limit_dependency)
):
    """
    删除指定的会话

    Args:
        session_id: 会话ID

    Returns:
        删除结果
    """
    try:
        # 验证会话ID
        validated_session_id = InputValidator.validate_session_id(session_id)

        # 检查会话是否存在
        session_info = get_session_info(validated_session_id)
        if not session_info:
            raise SessionError("会话不存在", validated_session_id)

        # 删除会话数据
        delete_session_data(validated_session_id)

        return ResponseBuilder.success(data={"session_id": validated_session_id}, message=f"会话 {validated_session_id} 已删除")

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise SessionError("删除会话失败", validated_session_id, {"error": str(e)})


@router.get("/sessions", summary="获取会话列表")
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: None = Depends(rate_limit_dependency)
):
    """
    获取会话列表

    Args:
        page: 页码
        page_size: 每页大小

    Returns:
        会话列表
    """
    try:
        # 获取所有会话
        all_sessions = list_all_sessions()
        
        # 计算分页
        total = len(all_sessions)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_sessions = all_sessions[start_idx:end_idx]

        # 转换为SessionInfo格式
        session_infos = []
        for session_data in paginated_sessions:
            session_id = session_data.get("session_id")
            session_info = get_session_info(session_id)
            
            if session_info:
                # 计算对话轮数
                messages = get_session_messages(session_id, limit=1000)
                total_turns = len([msg for msg in messages if msg["role"] == "user"])
                
                # 计算持续时间（分钟）
                created_at = session_info.get("created_at", datetime.now())
                last_activity = session_info.get("last_activity", datetime.now())
                duration_minutes = int((last_activity - created_at).total_seconds() / 60) if last_activity > created_at else 0
                
                # 检查是否活跃（24小时内有活动）
                is_active = (datetime.now() - last_activity).total_seconds() < 24 * 3600
                
                session_info_obj = SessionInfo(
                    session_id=session_id,
                    start_time=created_at,
                    last_update=last_activity,
                    total_turns=total_turns,
                    duration_minutes=duration_minutes,
                    is_active=is_active
                )
                session_infos.append(session_info_obj)

        # 使用响应构建器
        return ResponseBuilder.paginated(
            data=session_infos,
            total=total,
            page=page,
            page_size=page_size,
            message="获取会话列表成功"
        )

    except Exception as e:
        raise SessionError("获取会话列表失败", "", {"error": str(e)})


# 辅助函数
async def save_conversation_turn(
    session_id: str,
    turn_id: str,
    user_message: str,
    ai_response: str,
    processing_time: float
):
    """
    保存对话轮次到记忆系统
    """
    try:
        # TODO: 实际的记忆保存逻辑
        print(f"保存对话轮次: {turn_id} - {processing_time:.2f}s")
    except Exception as e:
        print(f"保存对话轮次失败: {e}")
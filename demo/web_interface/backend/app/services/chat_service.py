"""
聊天服务
处理对话相关的业务逻辑
"""

import asyncio
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from app.models.chat import (
    ChatRequest, ChatResponse, ConversationTurn, ChatState,
    SearchRequest, SearchResult, ToolExecutionRequest, ToolExecutionResponse
)
from app.core.exceptions import ValidationError, AIServiceError, SessionError
from app.core.security import InputValidator
from app.utils.ai_partner import get_ai_partner_service

logger = logging.getLogger(__name__)


class ChatService:
    """聊天服务类"""

    def __init__(self):
        """初始化聊天服务"""
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.ai_partner = get_ai_partner_service()

    async def process_message(self, request: ChatRequest) -> ChatResponse:
        """
        处理用户消息

        Args:
            request: 聊天请求

        Returns:
            聊天响应
        """
        try:
            # 验证输入
            sanitized_message = InputValidator.sanitize_message(request.message)

            # 生成或验证会话ID
            session_id = request.session_id or self._generate_session_id()

            # 更新会话活动时间
            self._update_session_activity(session_id)

            # 构建上下文信息
            context_info = self._build_context_info(
                session_id,
                request.context_turns,
                request.enable_search,
                request.enable_tools
            )

            # 调用AI Partner
            ai_result = await self.ai_partner.chat(
                sanitized_message,
                session_id
            )

            if not ai_result.get("success"):
                raise AIServiceError(
                    ai_result.get("error", "AI服务调用失败"),
                    "chat_processing",
                    ai_result
                )

            # 构建响应
            response = ChatResponse(
                response=ai_result["response"],
                session_id=session_id,
                timestamp=datetime.now(),
                processing_time=ai_result.get("processing_time", 0.0),
                context_used=context_info["context_used"],
                search_results=context_info["search_results"],
                tool_calls=context_info["tool_calls"],
                metadata={
                    "turn_id": self._generate_turn_id(),
                    "model": self.ai_partner.config.get("llm_model", "glm-4.6"),
                    "temperature": self.ai_partner.config.get("llm_temperature", 0.7),
                    "ai_partner_metadata": ai_result.get("metadata", {}),
                    "user_metadata": request.user_metadata or {}
                }
            )

            # 更新会话状态
            self._update_session_state(session_id, request, response)

            return response

        except ValidationError:
            raise
        except AIServiceError:
            raise
        except Exception as e:
            logger.error(f"消息处理失败: {e}")
            raise AIServiceError("消息处理失败", "chat_service", {"error": str(e)})

    async def get_session_state(self, session_id: str) -> ChatState:
        """
        获取会话状态

        Args:
            session_id: 会话ID

        Returns:
            会话状态
        """
        try:
            # 验证会话ID
            validated_session_id = InputValidator.validate_session_id(session_id)

            # 获取会话信息
            session_info = self.active_sessions.get(validated_session_id, {})

            # 获取AI Partner会话信息
            ai_session_info = self.ai_partner.get_session_info()

            # 构建状态对象
            state = ChatState(
                session_id=validated_session_id,
                current_turn=session_info.get("turn_count", 0),
                context_summary=session_info.get("context_summary", ""),
                persona_active=ai_session_info.get("persona_validation", {}).get("user_persona_exists", False),
                vector_store_connected=ai_session_info.get("vector_store_stats", {}).get("total_chunks", 0) > 0,
                memory_connected=ai_session_info.get("memory_stats", {}).get("total_sessions", 0) > 0,
                last_activity=session_info.get("last_activity", datetime.now()),
                active_tools=session_info.get("active_tools", ["weather", "calculator"])
            )

            return state

        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(f"获取会话状态失败: {e}")
            raise SessionError("获取会话状态失败", session_id, {"error": str(e)})

    async def search_knowledge(self, request: SearchRequest) -> List[SearchResult]:
        """
        搜索知识库

        Args:
            request: 搜索请求

        Returns:
            搜索结果列表
        """
        try:
            # 验证搜索查询
            validated_query = InputValidator.validate_query(request.query)

            # 调用AI Partner的搜索功能
            raw_results = self.ai_partner.search_knowledge(
                validated_query,
                request.top_k
            )

            # 转换为SearchResult模型
            results = []
            for raw_result in raw_results:
                if raw_result.get("similarity", 0) >= request.min_score:
                    result = SearchResult(
                        content=raw_result.get("content", ""),
                        metadata=raw_result.get("metadata", {}),
                        similarity=raw_result.get("similarity", 0.0),
                        distance=raw_result.get("distance", 1.0),
                        chunk_id=raw_result.get("metadata", {}).get("chunk_id")
                    )
                    results.append(result)

            return results

        except ValueError as e:
            raise ValidationError(str(e))
        except Exception as e:
            logger.error(f"知识搜索失败: {e}")
            raise AIServiceError("知识搜索失败", "knowledge_search", {"error": str(e)})

    async def execute_tool(self, request: ToolExecutionRequest) -> ToolExecutionResponse:
        """
        执行工具

        Args:
            request: 工具执行请求

        Returns:
            工具执行结果
        """
        try:
            start_time = datetime.now()

            # 根据工具名称执行相应的逻辑
            if request.tool_name == "calculator":
                result = await self._execute_calculator(request.parameters)
            elif request.tool_name == "weather":
                result = await self._execute_weather(request.parameters)
            else:
                raise ValueError(f"未知的工具: {request.tool_name}")

            processing_time = (datetime.now() - start_time).total_seconds()

            response = ToolExecutionResponse(
                tool_name=request.tool_name,
                success=True,
                result=result,
                execution_time=processing_time,
                metadata={
                    "parameters": request.parameters,
                    "session_id": request.session_id
                }
            )

            return response

        except ValueError as e:
            raise AIServiceError(f"工具执行失败: {str(e)}", request.tool_name)
        except Exception as e:
            logger.error(f"工具执行失败: {e}")
            raise AIServiceError("工具执行失败", request.tool_name, {"error": str(e)})

    def _generate_session_id(self) -> str:
        """生成会话ID"""
        return f"session_{uuid.uuid4().hex[:12]}"

    def _generate_turn_id(self) -> str:
        """生成轮次ID"""
        return f"turn_{uuid.uuid4().hex[:12]}"

    def _update_session_activity(self, session_id: str):
        """更新会话活动时间"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = {
                "created_at": datetime.now(),
                "turn_count": 0,
                "active_tools": []
            }

        self.active_sessions[session_id]["last_activity"] = datetime.now()

    def _build_context_info(
        self,
        session_id: str,
        context_turns: int,
        enable_search: bool,
        enable_tools: bool
    ) -> Dict[str, Any]:
        """构建上下文信息"""
        context_info = {
            "context_used": [],
            "search_results": [],
            "tool_calls": []
        }

        # 获取画像上下文
        try:
            persona_context = self.ai_partner.get_persona_context()
            if persona_context and persona_context != "暂无画像信息":
                context_info["context_used"].append("用户画像")
        except Exception as e:
            logger.warning(f"获取画像上下文失败: {e}")

        # 模拟搜索结果（如果启用）
        if enable_search:
            # 这里可以添加实际的搜索逻辑
            context_info["context_used"].append("知识库检索")
            context_info["search_results"] = [
                {
                    "content": "模拟搜索结果",
                    "metadata": {"source": "knowledge_base"},
                    "similarity": 0.85
                }
            ]

        # 模拟工具调用（如果启用）
        if enable_tools:
            context_info["context_used"].append("工具调用")
            context_info["tool_calls"] = [
                {
                    "tool_name": "example_tool",
                    "parameters": {"param": "value"},
                    "result": "工具执行结果"
                }
            ]

        return context_info

    def _update_session_state(
        self,
        session_id: str,
        request: ChatRequest,
        response: ChatResponse
    ):
        """更新会话状态"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session["turn_count"] += 1

            # 更新上下文摘要
            if len(request.message) > 50:
                summary = request.message[:50] + "..."
            else:
                summary = request.message
            session["context_summary"] = summary

    async def _execute_calculator(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行计算器工具"""
        try:
            expression = parameters.get("expression", "")
            if not expression:
                raise ValueError("缺少表达式参数")

            # 安全计算（简单实现）
            import re
            if not re.match(r'^[\d+\-*/().\s]+$', expression):
                raise ValueError("表达式包含不支持的字符")

            result = eval(expression)

            return {
                "expression": expression,
                "result": result,
                "type": "number" if isinstance(result, (int, float)) else "other"
            }

        except Exception as e:
            raise ValueError(f"计算错误: {str(e)}")

    async def _execute_weather(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """执行天气查询工具"""
        try:
            city = parameters.get("city", "北京")

            # 模拟天气数据
            import random
            weather_data = {
                "city": city,
                "temperature": random.randint(-10, 35),
                "condition": random.choice(["晴天", "多云", "阴天", "小雨"]),
                "humidity": random.randint(30, 90),
                "wind_speed": random.randint(0, 20),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            return weather_data

        except Exception as e:
            raise ValueError(f"天气查询错误: {str(e)}")

    def get_active_sessions_count(self) -> int:
        """获取活跃会话数量"""
        # 清理过期会话（1小时未活动）
        cutoff_time = datetime.now() - timedelta(hours=1)
        expired_sessions = [
            sid for sid, session in self.active_sessions.items()
            if session.get("last_activity", datetime.min) < cutoff_time
        ]

        for sid in expired_sessions:
            del self.active_sessions[sid]

        return len(self.active_sessions)

    def cleanup_old_sessions(self, hours: int = 24) -> int:
        """清理旧会话"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        old_sessions = [
            sid for sid, session in self.active_sessions.items()
            if session.get("last_activity", datetime.min) < cutoff_time
        ]

        for sid in old_sessions:
            del self.active_sessions[sid]

        return len(old_sessions)


# 全局服务实例
_chat_service: Optional[ChatService] = None


def get_chat_service() -> ChatService:
    """获取聊天服务实例"""
    global _chat_service
    if _chat_service is None:
        _chat_service = ChatService()
    return _chat_service
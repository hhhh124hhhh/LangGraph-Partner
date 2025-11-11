"""
聊天相关的数据模型
定义API请求和响应的数据结构
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class ChatRequest(BaseModel):
    """聊天请求模型"""

    message: str = Field(..., description="用户消息内容", min_length=1, max_length=10000)
    session_id: Optional[str] = Field(None, description="会话ID，如果不提供将创建新会话")
    context_turns: int = Field(default=5, ge=1, le=20, description="上下文轮次数量")
    enable_search: bool = Field(default=True, description="是否启用语义搜索")
    enable_tools: bool = Field(default=True, description="是否启用工具调用")
    user_metadata: Optional[Dict[str, Any]] = Field(default=None, description="用户元数据")

    @validator("message")
    def validate_message(cls, v):
        """验证消息内容"""
        if not v or not v.strip():
            raise ValueError("消息内容不能为空")
        return v.strip()


class ChatResponse(BaseModel):
    """聊天响应模型"""

    response: str = Field(..., description="AI回应内容")
    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(..., description="响应时间戳")
    processing_time: float = Field(..., description="处理耗时（秒）")
    context_used: List[str] = Field(default_factory=list, description="使用的上下文信息")
    search_results: List[Dict[str, Any]] = Field(default_factory=list, description="搜索结果")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="工具调用记录")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


class SessionInfo(BaseModel):
    """会话信息模型"""

    session_id: str = Field(..., description="会话ID")
    start_time: datetime = Field(..., description="会话开始时间")
    last_update: datetime = Field(..., description="最后更新时间")
    total_turns: int = Field(..., description="对话轮次总数")
    duration_minutes: float = Field(..., description="会话持续时间（分钟）")
    is_active: bool = Field(default=True, description="会话是否活跃")


class ConversationTurn(BaseModel):
    """对话轮次模型"""

    turn_id: str = Field(..., description="轮次ID")
    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(..., description="时间戳")
    user_message: str = Field(..., description="用户消息")
    ai_response: str = Field(..., description="AI回应")
    context_used: List[str] = Field(default_factory=list, description="使用的上下文")
    tools_called: List[Dict[str, Any]] = Field(default_factory=list, description="调用的工具")
    search_query: Optional[str] = Field(None, description="搜索查询")
    retrieval_count: int = Field(default=0, description="检索结果数量")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="其他元数据")


class ChatState(BaseModel):
    """聊天状态模型"""

    session_id: str = Field(..., description="会话ID")
    current_turn: int = Field(default=0, description="当前轮次")
    context_summary: str = Field(default="", description="上下文摘要")
    persona_active: bool = Field(default=True, description="画像是否激活")
    vector_store_connected: bool = Field(default=True, description="向量存储连接状态")
    memory_connected: bool = Field(default=True, description="记忆系统连接状态")
    last_activity: datetime = Field(..., description="最后活动时间")
    active_tools: List[str] = Field(default_factory=list, description="激活的工具列表")


class StreamChunk(BaseModel):
    """流式响应块模型"""

    chunk_type: str = Field(..., description="块类型：message, metadata, error, complete")
    content: str = Field(default="", description="内容")
    session_id: Optional[str] = Field(None, description="会话ID")
    turn_id: Optional[str] = Field(None, description="轮次ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

    @validator("chunk_type")
    def validate_chunk_type(cls, v):
        """验证块类型"""
        valid_types = ["message", "metadata", "error", "complete"]
        if v not in valid_types:
            raise ValueError(f"块类型必须是以下之一: {valid_types}")
        return v


class ChatHistoryRequest(BaseModel):
    """聊天历史请求模型"""

    session_id: str = Field(..., description="会话ID")
    limit: int = Field(default=10, ge=1, le=100, description="返回的轮次数量限制")
    offset: int = Field(default=0, ge=0, description="偏移量")
    include_metadata: bool = Field(default=True, description="是否包含元数据")


class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""

    session_id: str = Field(..., description="会话ID")
    total_turns: int = Field(..., description="总轮次数")
    turns: List[ConversationTurn] = Field(..., description="对话轮次列表")
    has_more: bool = Field(default=False, description="是否有更多数据")
    next_offset: Optional[int] = Field(None, description="下一页偏移量")


class SearchRequest(BaseModel):
    """搜索请求模型"""

    query: str = Field(..., description="搜索查询", min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    min_score: float = Field(default=0.3, ge=0.0, le=1.0, description="最小相似度阈值")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="过滤条件")


class SearchResult(BaseModel):
    """搜索结果模型"""

    content: str = Field(..., description="文档内容")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    similarity: float = Field(..., description="相似度分数")
    distance: float = Field(..., description="距离分数")
    chunk_id: Optional[str] = Field(None, description="文档块ID")


class ToolExecutionRequest(BaseModel):
    """工具执行请求模型"""

    tool_name: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(..., description="工具参数")
    session_id: Optional[str] = Field(None, description="会话ID")


class ToolExecutionResponse(BaseModel):
    """工具执行响应模型"""

    tool_name: str = Field(..., description="工具名称")
    success: bool = Field(..., description="是否执行成功")
    result: Any = Field(..., description="执行结果")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(..., description="执行耗时（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
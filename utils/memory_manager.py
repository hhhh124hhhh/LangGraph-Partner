"""
对话记忆管理系统
管理短期和长期对话记忆，维护上下文连贯性
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import pickle


@dataclass
class ConversationTurn:
    """单次对话轮次"""
    timestamp: datetime
    user_message: str
    ai_response: str
    context_used: List[str] = None  # 使用的上下文（笔记、画像等）
    tools_called: List[str] = None   # 调用的工具
    metadata: Dict = None           # 其他元数据

    def __post_init__(self):
        if self.context_used is None:
            self.context_used = []
        if self.tools_called is None:
            self.tools_called = []
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ConversationSession:
    """对话会话"""
    session_id: str
    start_time: datetime
    last_update: datetime
    turns: List[ConversationTurn]
    session_metadata: Dict = None

    def __post_init__(self):
        if self.session_metadata is None:
            self.session_metadata = {}

    def add_turn(self, user_message: str, ai_response: str, **kwargs) -> ConversationTurn:
        """添加新的对话轮次"""
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_message=user_message,
            ai_response=ai_response,
            **kwargs
        )
        self.turns.append(turn)
        self.last_update = datetime.now()
        return turn

    def get_recent_turns(self, count: int = 5) -> List[ConversationTurn]:
        """获取最近的对话轮次"""
        return self.turns[-count:] if count > 0 else []

    def get_context_summary(self, max_turns: int = 10) -> str:
        """获取对话上下文摘要"""
        recent_turns = self.get_recent_turns(max_turns)
        if not recent_turns:
            return "暂无对话历史"

        summary_parts = []
        for i, turn in enumerate(recent_turns):
            summary_parts.append(
                f"轮次 {i+1}:\n"
                f"用户: {turn.user_message}\n"
                f"AI: {turn.ai_response}\n"
            )

        return "\n".join(summary_parts)


class MemoryManager:
    """记忆管理器"""

    def __init__(self, memory_dir: str = "./memory"):
        """
        初始化记忆管理器

        Args:
            memory_dir: 记忆存储目录
        """
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)

        # 文件路径
        self.sessions_file = self.memory_dir / "sessions.pkl"
        self.current_session_file = self.memory_dir / "current_session.json"

        # 当前活跃会话
        self.current_session: Optional[ConversationSession] = None

        # 加载现有数据
        self._load_memory()

    def _load_memory(self):
        """加载存储的记忆数据"""
        try:
            # 加载会话历史
            if self.sessions_file.exists():
                with open(self.sessions_file, 'rb') as f:
                    self.sessions = pickle.load(f)
            else:
                self.sessions = {}

            # 加载当前会话
            if self.current_session_file.exists():
                with open(self.current_session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 转换字符串时间为 datetime 对象
                    start_time = datetime.fromisoformat(data['start_time'])
                    last_update = datetime.fromisoformat(data['last_update'])

                    # 重建会话对象
                    self.current_session = ConversationSession(
                        session_id=data['session_id'],
                        start_time=start_time,
                        last_update=last_update,
                        turns=[],  # 不加载详细历史，只保留会话信息
                        session_metadata=data.get('session_metadata', {})
                    )
        except Exception as e:
            print(f"加载记忆数据失败: {e}")
            self.sessions = {}
            self.current_session = None

    def _save_memory(self):
        """保存记忆数据"""
        try:
            # 保存会话历史
            with open(self.sessions_file, 'wb') as f:
                pickle.dump(self.sessions, f)

            # 保存当前会话
            if self.current_session:
                session_data = {
                    'session_id': self.current_session.session_id,
                    'start_time': self.current_session.start_time.isoformat(),
                    'last_update': self.current_session.last_update.isoformat(),
                    'session_metadata': self.current_session.session_metadata
                }

                with open(self.current_session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存记忆数据失败: {e}")

    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        创建新的对话会话

        Args:
            session_id: 可选的会话ID，如果不提供则自动生成

        Returns:
            新创建的会话ID
        """
        if session_id is None:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 保存当前会话（如果存在）
        if self.current_session:
            self.sessions[self.current_session.session_id] = self.current_session

        # 创建新会话
        self.current_session = ConversationSession(
            session_id=session_id,
            start_time=datetime.now(),
            last_update=datetime.now(),
            turns=[]
        )

        self._save_memory()
        return session_id

    def add_conversation_turn(
        self,
        user_message: str,
        ai_response: str,
        context_used: List[str] = None,
        tools_called: List[str] = None,
        **metadata
    ) -> bool:
        """
        添加对话轮次

        Args:
            user_message: 用户消息
            ai_response: AI 回应
            context_used: 使用的上下文
            tools_called: 调用的工具
            **metadata: 其他元数据

        Returns:
            是否添加成功
        """
        if not self.current_session:
            self.create_session()

        try:
            turn = self.current_session.add_turn(
                user_message=user_message,
                ai_response=ai_response,
                context_used=context_used or [],
                tools_called=tools_called or [],
                metadata=metadata
            )

            # 保存到会话历史
            self.sessions[self.current_session.session_id] = self.current_session

            self._save_memory()
            return True
        except Exception as e:
            print(f"添加对话轮次失败: {e}")
            return False

    def get_current_context(self, max_turns: int = 5) -> str:
        """
        获取当前对话上下文

        Args:
            max_turns: 最大轮次数

        Returns:
            格式化的上下文字符串
        """
        if not self.current_session:
            return "当前没有活跃的对话会话"

        return self.current_session.get_context_summary(max_turns)

    def search_conversations(
        self,
        query: str,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        搜索对话历史

        Args:
            query: 搜索查询
            session_id: 可选的会话ID限制
            limit: 结果数量限制

        Returns:
            匹配的对话轮次列表
        """
        results = []
        sessions_to_search = [session_id] if session_id else list(self.sessions.keys())

        for sid in sessions_to_search:
            if sid not in self.sessions:
                continue

            session = self.sessions[sid]
            for turn in session.turns:
                # 简单的关键词匹配（可以升级为语义搜索）
                if (query.lower() in turn.user_message.lower() or
                    query.lower() in turn.ai_response.lower()):

                    results.append({
                        'session_id': sid,
                        'timestamp': turn.timestamp.isoformat(),
                        'user_message': turn.user_message,
                        'ai_response': turn.ai_response,
                        'context_used': turn.context_used,
                        'tools_called': turn.tools_called
                    })

                    if len(results) >= limit:
                        break

            if len(results) >= limit:
                break

        return results

    def get_session_info(self, session_id: Optional[str] = None) -> Dict:
        """
        获取会话信息

        Args:
            session_id: 会话ID，如果不提供则返回当前会话信息

        Returns:
            会话信息字典
        """
        session = self.current_session
        if session_id:
            session = self.sessions.get(session_id)

        if not session:
            return {}

        return {
            'session_id': session.session_id,
            'start_time': session.start_time.isoformat(),
            'last_update': session.last_update.isoformat(),
            'total_turns': len(session.turns),
            'duration_minutes': (session.last_update - session.start_time).total_seconds() / 60
        }

    def list_sessions(self, limit: int = 20) -> List[Dict]:
        """
        列出所有会话

        Args:
            limit: 返回的会话数量限制

        Returns:
            会话信息列表
        """
        sessions_info = []

        for session_id, session in self.sessions.items():
            sessions_info.append({
                'session_id': session_id,
                'start_time': session.start_time.isoformat(),
                'last_update': session.last_update.isoformat(),
                'total_turns': len(session.turns)
            })

        # 按最后更新时间排序
        sessions_info.sort(key=lambda x: x['last_update'], reverse=True)

        return sessions_info[:limit]

    def clear_old_sessions(self, days: int = 30) -> int:
        """
        清除旧的会话记录

        Args:
            days: 保留天数

        Returns:
            清除的会话数量
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        old_sessions = []

        for session_id, session in self.sessions.items():
            if session.last_update < cutoff_date:
                old_sessions.append(session_id)

        for session_id in old_sessions:
            del self.sessions[session_id]

        self._save_memory()
        return len(old_sessions)

    def switch_session(self, session_id: str) -> bool:
        """
        切换到指定会话

        Args:
            session_id: 目标会话ID

        Returns:
            是否切换成功
        """
        if session_id not in self.sessions:
            return False

        # 保存当前会话
        if self.current_session:
            self.sessions[self.current_session.session_id] = self.current_session

        # 切换会话
        self.current_session = self.sessions[session_id]
        self._save_memory()
        return True

    def get_memory_stats(self) -> Dict:
        """
        获取记忆统计信息

        Returns:
            统计信息字典
        """
        total_sessions = len(self.sessions)
        total_turns = sum(len(session.turns) for session in self.sessions.values())

        current_session_info = self.get_session_info() if self.current_session else {}

        return {
            'total_sessions': total_sessions,
            'total_turns': total_turns,
            'current_session_id': self.current_session.session_id if self.current_session else None,
            'current_session_turns': current_session_info.get('total_turns', 0),
            'memory_dir': str(self.memory_dir)
        }


# 全局记忆管理器实例
_memory_manager = None


def get_memory_manager(memory_dir: str = "./memory") -> MemoryManager:
    """
    获取全局记忆管理器实例

    Args:
        memory_dir: 记忆存储目录

    Returns:
        MemoryManager 实例
    """
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(memory_dir)
    return _memory_manager


def add_conversation(user_message: str, ai_response: str, **kwargs) -> bool:
    """
    便捷函数：添加对话轮次

    Args:
        user_message: 用户消息
        ai_response: AI 回应
        **kwargs: 其他参数

    Returns:
        是否添加成功
    """
    manager = get_memory_manager()
    return manager.add_conversation_turn(user_message, ai_response, **kwargs)


def get_current_context(max_turns: int = 5) -> str:
    """
    便捷函数：获取当前对话上下文

    Args:
        max_turns: 最大轮次数

    Returns:
        格式化的上下文
    """
    manager = get_memory_manager()
    return manager.get_current_context(max_turns)
"""
会话持久化管理模块

提供会话数据的持久化存储和检索功能，支持：
- 会话数据的保存和加载
- 会话历史管理
- 会话状态持久化
- 多种存储后端支持
"""

import json
import os
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import uuid
import logging

from ..core.config import settings
from ..core.exceptions import SessionError, MemoryError

logger = logging.getLogger(__name__)


class SessionPersistence:
    """会话持久化管理器"""
    
    def __init__(self, storage_dir: Optional[str] = None):
        """
        初始化会话持久化管理器
        
        Args:
            storage_dir: 存储目录路径
        """
        self.storage_dir = Path(storage_dir or settings.memory_dir) / "sessions"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # 会话索引文件
        self.index_file = self.storage_dir / "sessions_index.json"
        
        # 内存中的会话索引缓存
        self._session_index: Dict[str, Dict[str, Any]] = {}
        
        # 加载会话索引
        self._load_session_index()
    
    def _load_session_index(self):
        """加载会话索引"""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self._session_index = json.load(f)
            else:
                self._session_index = {}
        except Exception as e:
            logger.error(f"加载会话索引失败: {e}")
            self._session_index = {}
    
    def _save_session_index(self):
        """保存会话索引"""
        try:
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(self._session_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存会话索引失败: {e}")
            raise MemoryError("保存会话索引失败", "save_index")
    
    def create_session(self, session_id: Optional[str] = None, 
                      user_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        创建新会话
        
        Args:
            session_id: 会话ID，如果不提供则自动生成
            user_id: 用户ID
            metadata: 会话元数据
            
        Returns:
            会话ID
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 检查会话是否已存在
        if session_id in self._session_index:
            raise SessionError("会话已存在", session_id)
        
        # 创建会话数据
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "message_count": 0,
            "status": "active",
            "metadata": metadata or {},
            "key_topics": [],
            "tags": []
        }
        
        # 保存到索引
        self._session_index[session_id] = session_data
        
        # 创建会话文件
        session_file = self.storage_dir / f"{session_id}.json"
        session_content = {
            "session_id": session_id,
            "messages": [],
            "context": {},
            "persona_context": "",
            "created_at": session_data["created_at"]
        }
        
        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_content, f, ensure_ascii=False, indent=2)
            
            # 保存索引
            self._save_session_index()
            
            logger.info(f"创建会话成功: {session_id}")
            return session_id
            
        except Exception as e:
            # 清理索引中的记录
            if session_id in self._session_index:
                del self._session_index[session_id]
            raise SessionError(f"创建会话失败: {str(e)}", session_id)
    
    def save_message(self, session_id: str, message: Dict[str, Any]) -> bool:
        """
        保存消息到会话
        
        Args:
            session_id: 会话ID
            message: 消息数据
            
        Returns:
            是否保存成功
        """
        if session_id not in self._session_index:
            raise SessionError("会话不存在", session_id)
        
        session_file = self.storage_dir / f"{session_id}.json"
        
        try:
            # 加载现有会话内容
            if session_file.exists():
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_content = json.load(f)
            else:
                session_content = {
                    "session_id": session_id,
                    "messages": [],
                    "context": {},
                    "persona_context": "",
                    "created_at": datetime.now().isoformat()
                }
            
            # 添加消息
            message["timestamp"] = datetime.now().isoformat()
            session_content["messages"].append(message)
            
            # 保存会话内容
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_content, f, ensure_ascii=False, indent=2)
            
            # 更新索引
            self._session_index[session_id]["updated_at"] = datetime.now().isoformat()
            self._session_index[session_id]["last_activity"] = datetime.now().isoformat()
            self._session_index[session_id]["message_count"] = len(session_content["messages"])
            
            # 保存索引
            self._save_session_index()
            
            return True
            
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
            raise MemoryError("保存消息失败", "save_message")
    
    def get_session_messages(self, session_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取会话消息
        
        Args:
            session_id: 会话ID
            limit: 消息数量限制
            
        Returns:
            消息列表
        """
        if session_id not in self._session_index:
            raise SessionError("会话不存在", session_id)
        
        session_file = self.storage_dir / f"{session_id}.json"
        
        try:
            if not session_file.exists():
                return []
            
            with open(session_file, 'r', encoding='utf-8') as f:
                session_content = json.load(f)
            
            messages = session_content.get("messages", [])
            
            if limit:
                messages = messages[-limit:]
            
            return messages
            
        except Exception as e:
            logger.error(f"获取会话消息失败: {e}")
            raise MemoryError("获取会话消息失败", "load_messages")
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话信息
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话信息
        """
        if session_id not in self._session_index:
            raise SessionError("会话不存在", session_id)
        
        session_info = self._session_index[session_id].copy()
        
        # 添加消息统计
        try:
            messages = self.get_session_messages(session_id)
            session_info["actual_message_count"] = len(messages)
            
            # 计算关键主题
            user_messages = [msg for msg in messages if msg.get("role") == "user"]
            if user_messages:
                # 简单的关键词提取
                all_text = " ".join([msg.get("content", "") for msg in user_messages])
                # 这里可以集成更复杂的NLP分析
                session_info["key_topics"] = self._extract_key_topics(all_text)
                
        except Exception as e:
            logger.error(f"获取会话统计失败: {e}")
        
        return session_info
    
    def _extract_key_topics(self, text: str, max_topics: int = 5) -> List[str]:
        """
        提取关键主题（简单实现）
        
        Args:
            text: 输入文本
            max_topics: 最大主题数
            
        Returns:
            主题列表
        """
        # 简单的关键词提取（可以替换为更复杂的NLP算法）
        common_keywords = [
            "LangGraph", "AI", "智能体", "开发", "代码", "API", "数据库",
            "前端", "后端", "部署", "测试", "优化", "性能", "架构"
        ]
        
        topics = []
        text_lower = text.lower()
        
        for keyword in common_keywords:
            if keyword.lower() in text_lower:
                topics.append(keyword)
                if len(topics) >= max_topics:
                    break
        
        return topics
    
    def list_sessions(self, user_id: Optional[str] = None, 
                     status: Optional[str] = None,
                     limit: int = 50) -> List[Dict[str, Any]]:
        """
        列出会话
        
        Args:
            user_id: 用户ID过滤
            status: 状态过滤
            limit: 数量限制
            
        Returns:
            会话列表
        """
        sessions = []
        
        for session_id, session_data in self._session_index.items():
            # 应用过滤条件
            if user_id and session_data.get("user_id") != user_id:
                continue
            
            if status and session_data.get("status") != status:
                continue
            
            sessions.append(session_data.copy())
        
        # 按最后活动时间排序
        sessions.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        
        return sessions[:limit]
    
    def update_session_metadata(self, session_id: str, 
                              metadata: Dict[str, Any]) -> bool:
        """
        更新会话元数据
        
        Args:
            session_id: 会话ID
            metadata: 元数据
            
        Returns:
            是否更新成功
        """
        if session_id not in self._session_index:
            raise SessionError("会话不存在", session_id)
        
        try:
            # 更新索引中的元数据
            self._session_index[session_id]["metadata"].update(metadata)
            self._session_index[session_id]["updated_at"] = datetime.now().isoformat()
            
            # 保存索引
            self._save_session_index()
            
            return True
            
        except Exception as e:
            logger.error(f"更新会话元数据失败: {e}")
            return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            是否删除成功
        """
        if session_id not in self._session_index:
            raise SessionError("会话不存在", session_id)
        
        try:
            # 删除会话文件
            session_file = self.storage_dir / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            # 从索引中删除
            del self._session_index[session_id]
            
            # 保存索引
            self._save_session_index()
            
            logger.info(f"删除会话成功: {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除会话失败: {e}")
            return False
    
    def cleanup_expired_sessions(self, days: int = 30) -> int:
        """
        清理过期会话
        
        Args:
            days: 保留天数
            
        Returns:
            清理的会话数量
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        cutoff_str = cutoff_date.isoformat()
        
        expired_sessions = []
        
        for session_id, session_data in self._session_index.items():
            last_activity = session_data.get("last_activity", "")
            if last_activity < cutoff_str:
                expired_sessions.append(session_id)
        
        # 删除过期会话
        deleted_count = 0
        for session_id in expired_sessions:
            try:
                if self.delete_session(session_id):
                    deleted_count += 1
            except Exception as e:
                logger.error(f"清理过期会话失败 {session_id}: {e}")
        
        logger.info(f"清理过期会话完成，删除 {deleted_count} 个会话")
        return deleted_count
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """
        获取会话统计信息
        
        Returns:
            统计信息
        """
        total_sessions = len(self._session_index)
        active_sessions = len([s for s in self._session_index.values() 
                              if s.get("status") == "active"])
        
        total_messages = sum(s.get("message_count", 0) 
                           for s in self._session_index.values())
        
        # 最近7天活跃会话
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_sessions = len([s for s in self._session_index.values()
                             if s.get("last_activity", "") > week_ago])
        
        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "total_messages": total_messages,
            "recent_sessions": recent_sessions,
            "storage_directory": str(self.storage_dir)
        }


# 全局会话持久化实例
_session_persistence: Optional[SessionPersistence] = None


def get_session_persistence() -> SessionPersistence:
    """获取会话持久化实例"""
    global _session_persistence
    
    if _session_persistence is None:
        _session_persistence = SessionPersistence()
    
    return _session_persistence


# 便捷函数
async def create_session(session_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
    """创建新会话"""
    persistence = get_session_persistence()
    return persistence.create_session(session_id, user_id, metadata)


async def save_message(session_id: str, message: Dict[str, Any]) -> bool:
    """保存消息"""
    persistence = get_session_persistence()
    return persistence.save_message(session_id, message)


async def get_session_messages(session_id: str, 
                              limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """获取会话消息"""
    persistence = get_session_persistence()
    return persistence.get_session_messages(session_id, limit)


async def get_session_info(session_id: str) -> Dict[str, Any]:
    """获取会话信息"""
    persistence = get_session_persistence()
    return persistence.get_session_info(session_id)


async def delete_session(session_id: str) -> bool:
    """删除会话"""
    persistence = get_session_persistence()
    return persistence.delete_session(session_id)


async def list_all_sessions(limit: int = 100) -> List[Dict[str, Any]]:
    """列出所有会话"""
    persistence = get_session_persistence()
    return persistence.list_sessions(limit=limit)
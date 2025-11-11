"""对话记忆管理测试"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import json
from utils.memory_manager import MemoryManager


class TestMemoryManager:
    """记忆管理系统测试类"""
    
    @patch('os.makedirs')
    def setup_method(self, mock_makedirs):
        """设置测试环境"""
        # 创建MemoryManager实例
        self.memory_manager = MemoryManager(memory_dir="./test_memory")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_conversation(self, mock_json_dump, mock_open_file):
        """测试保存对话"""
        # 测试数据
        session_id = "test_session_123"
        conversation = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
        ]
        
        # 调用方法
        self.memory_manager.save_conversation(session_id, conversation)
        
        # 验证文件操作
        mock_open_file.assert_called_once_with(
            f"./test_memory/{session_id}.json", "w", encoding="utf-8"
        )
        mock_json_dump.assert_called_once_with(
            conversation, mock_open_file.return_value.__enter__.return_value,
            ensure_ascii=False, indent=2
        )
    
    @patch('os.path.exists', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data='''[
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
    ]''')
    @patch('json.load')
    def test_load_conversation(self, mock_json_load, mock_open_file, mock_path_exists):
        """测试加载对话"""
        # 模拟JSON加载结果
        mock_conversation = [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "你好！有什么可以帮助你的？"}
        ]
        mock_json_load.return_value = mock_conversation
        
        # 调用方法
        result = self.memory_manager.load_conversation("test_session_123")
        
        # 验证结果
        assert result == mock_conversation
        mock_open_file.assert_called_once_with(
            f"./test_memory/test_session_123.json", "r", encoding="utf-8"
        )
    
    @patch('os.path.exists', return_value=False)
    def test_load_nonexistent_conversation(self, mock_path_exists):
        """测试加载不存在的对话"""
        result = self.memory_manager.load_conversation("nonexistent_session")
        assert result == []
    
    @patch('os.listdir')
    def test_list_sessions(self, mock_listdir):
        """测试列出所有会话"""
        # 模拟目录内容
        mock_listdir.return_value = [
            "session_1.json", "session_2.json", "other_file.txt"
        ]
        
        # 调用方法
        result = self.memory_manager.list_sessions()
        
        # 验证结果
        assert sorted(result) == ["session_1", "session_2"]
    
    @patch('os.path.exists', return_value=True)
    @patch('os.remove')
    def test_delete_session(self, mock_remove, mock_path_exists):
        """测试删除会话"""
        # 调用方法
        result = self.memory_manager.delete_session("session_to_delete")
        
        # 验证结果
        assert result is True
        mock_remove.assert_called_once_with(
            "./test_memory/session_to_delete.json"
        )
    
    @patch('os.path.exists', return_value=False)
    def test_delete_nonexistent_session(self, mock_path_exists):
        """测试删除不存在的会话"""
        result = self.memory_manager.delete_session("nonexistent_session")
        assert result is False
    
    def test_get_recent_conversations(self):
        """测试获取最近的对话"""
        # 模拟完整对话
        full_conversation = [
            {"role": "user", "content": "问题1"},
            {"role": "assistant", "content": "回答1"},
            {"role": "user", "content": "问题2"},
            {"role": "assistant", "content": "回答2"},
            {"role": "user", "content": "问题3"},
            {"role": "assistant", "content": "回答3"}
        ]
        
        # 调用方法，获取最近4条消息
        result = self.memory_manager.get_recent_conversations(
            full_conversation, max_messages=4
        )
        
        # 验证结果
        assert len(result) == 4
        assert result[0]["content"] == "问题2"
        assert result[-1]["content"] == "回答3"
"""LLM配置管理测试"""

import pytest
import os
from unittest.mock import patch, MagicMock
from utils.llm import get_llm_client, get_model_name, setup_llm


class TestLLMUtils:
    """LLM工具函数测试类"""
    
    @patch('utils.llm.openai.OpenAI')
    @patch('os.getenv')
    def test_get_llm_client_success(self, mock_getenv, mock_openai):
        """测试成功获取LLM客户端"""
        # 模拟环境变量
        mock_getenv.side_effect = lambda x: {
            'AI_CLAUDE_API_KEY': 'test_api_key',
            'AI_CLAUDE_BASE_URL': 'https://test-base-url.com'
        }.get(x)
        
        # 模拟OpenAI客户端
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # 调用函数
        client = get_llm_client()
        
        # 验证结果
        mock_openai.assert_called_once_with(
            api_key='test_api_key',
            base_url='https://test-base-url.com'
        )
        assert client == mock_client
    
    @patch('os.getenv', return_value=None)
    def test_get_llm_client_missing_api_key(self, mock_getenv):
        """测试缺少API密钥时的行为"""
        with pytest.raises(ValueError, match="API密钥未设置"):
            get_llm_client()
    
    @patch('os.getenv')
    def test_get_model_name(self, mock_getenv):
        """测试获取模型名称"""
        # 测试默认值
        mock_getenv.return_value = None
        assert get_model_name() == "glm-4.6"
        
        # 测试自定义值
        mock_getenv.return_value = "custom-model-123"
        assert get_model_name() == "custom-model-123"
    
    @patch('utils.llm.get_llm_client')
    @patch('utils.llm.get_model_name')
    def test_setup_llm(self, mock_get_model_name, mock_get_llm_client):
        """测试设置LLM"""
        # 模拟返回值
        mock_client = MagicMock()
        mock_get_llm_client.return_value = mock_client
        mock_get_model_name.return_value = "test-model"
        
        # 调用函数
        result = setup_llm()
        
        # 验证结果 - 确保返回了一个字典包含client和model_name
        assert isinstance(result, dict)
        assert 'client' in result
        assert 'model_name' in result
        assert result['client'] == mock_client
        assert result['model_name'] == "test-model"
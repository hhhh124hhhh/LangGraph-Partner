"""向量存储系统测试"""

import pytest
from unittest.mock import patch, MagicMock, mock_open
import chromadb
from utils.vector_store import VectorStore


class TestVectorStore:
    """向量存储系统测试类"""
    
    @patch('chromadb.PersistentClient')
    def setup_method(self, mock_persistent_client):
        """设置测试环境"""
        # 模拟ChromaDB客户端
        self.mock_client = MagicMock()
        mock_persistent_client.return_value = self.mock_client
        
        # 模拟集合
        self.mock_collection = MagicMock()
        self.mock_client.get_or_create_collection.return_value = self.mock_collection
        
        # 创建VectorStore实例
        self.vector_store = VectorStore(collection_name="test_collection")
    
    def test_initialization(self):
        """测试向量存储初始化"""
        # 验证调用
        self.mock_client.get_or_create_collection.assert_called_once_with(
            name="test_collection"
        )
    
    def test_add_document(self):
        """测试添加文档"""
        # 测试数据
        document = "这是测试文档内容"
        metadata = {"source": "test.md"}
        doc_id = "doc_123"
        
        # 调用方法
        self.vector_store.add_document(document, metadata, doc_id)
        
        # 验证调用
        self.mock_collection.add.assert_called_once()
        args, kwargs = self.mock_collection.add.call_args
        assert kwargs['documents'] == [document]
        assert kwargs['metadatas'] == [metadata]
        assert kwargs['ids'] == [doc_id]
    
    def test_search_documents(self):
        """测试搜索文档"""
        # 模拟搜索结果
        self.mock_collection.query.return_value = {
            "documents": ["文档1", "文档2"],
            "metadatas": [{"source": "doc1.md"}, {"source": "doc2.md"}],
            "distances": [0.1, 0.2]
        }
        
        # 调用方法
        results = self.vector_store.search_documents("测试查询", top_k=2)
        
        # 验证调用
        self.mock_collection.query.assert_called_once_with(
            query_texts=["测试查询"],
            n_results=2
        )
        
        # 验证结果格式
        assert len(results) == 2
        assert results[0]['document'] == "文档1"
        assert results[1]['distance'] == 0.2
    
    def test_clear_collection(self):
        """测试清空集合"""
        # 调用方法
        self.vector_store.clear_collection()
        
        # 验证调用
        self.mock_collection.delete.assert_called_once_with(where={})
    
    @patch('builtins.open', new_callable=mock_open, read_data="测试文件内容")
    def test_add_document_from_file(self, mock_file):
        """测试从文件添加文档"""
        # 调用方法
        self.vector_store.add_document_from_file("test_file.md")
        
        # 验证文件读取
        mock_file.assert_called_once_with("test_file.md", "r", encoding="utf-8")
        
        # 验证文档添加调用
        self.mock_collection.add.assert_called_once()
        args, kwargs = self.mock_collection.add.call_args
        assert kwargs['documents'] == ["测试文件内容"]
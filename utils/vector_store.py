"""
向量化存储系统
基于 ChromaDB 的语义搜索和检索功能
"""

import os
import sys
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
# 处理sentence-transformers与huggingface-hub版本兼容性问题
import sys
import warnings

# 先导入huggingface_hub，确保在导入sentence_transformers前解决兼容性问题
import huggingface_hub

# 检查并修复cached_download问题（huggingface-hub>=0.20.0中已移除）
if hasattr(huggingface_hub, 'hf_hub_download') and not hasattr(huggingface_hub, 'cached_download'):
    # 为huggingface_hub模块添加cached_download属性，指向hf_hub_download
    huggingface_hub.cached_download = huggingface_hub.hf_hub_download

# 现在导入sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
except ImportError as e:
    if "cannot import name 'cached_download'" in str(e):
        # 如果仍有问题，显示更详细的错误信息
        warnings.error("❌ sentence-transformers导入失败，请检查依赖版本。尝试: pip install --upgrade sentence-transformers huggingface-hub")
        raise
    else:
        raise
import numpy as np

# Add AI partner chat scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "ai-partner-chat" / "scripts"))

from chunk_schema import Chunk, validate_chunk


class VectorStore:
    """向量化存储管理器"""

    def __init__(self, db_path: str = "./vector_db"):
        """
        初始化向量存储

        Args:
            db_path: 向量数据库存储路径
        """
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)

        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # 初始化 embedding 模型（使用中文优化模型）
        self.embedding_model = SentenceTransformer('BAAI/bge-m3')

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(
            name="notes",
            metadata={"description": "用户笔记向量化存储"}
        )

    def _get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量嵌入

        Args:
            text: 输入文本

        Returns:
            向量嵌入列表
        """
        # BAAI/bge-m3 模型已经针对中文优化
        embedding = self.embedding_model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding.tolist()

    def _generate_chunk_id(self, filepath: str, chunk_id: int) -> str:
        """
        生成唯一的 chunk ID

        Args:
            filepath: 文件路径
            chunk_id: 文档内的 chunk ID

        Returns:
            唯一的 chunk ID
        """
        content = f"{filepath}:{chunk_id}"
        return hashlib.md5(content.encode()).hexdigest()

    def add_chunks(self, chunks: List[Chunk]) -> int:
        """
        添加文档块到向量存储

        Args:
            chunks: 文档块列表

        Returns:
            成功添加的数量
        """
        if not chunks:
            return 0

        validated_chunks = [chunk for chunk in chunks if validate_chunk(chunk)]
        if not validated_chunks:
            return 0

        ids = []
        embeddings = []
        documents = []
        metadatas = []

        for chunk in validated_chunks:
            chunk_id = self._generate_chunk_id(
                chunk['metadata']['filepath'],
                chunk['metadata']['chunk_id']
            )

            # 准备用于检索的文本（包含内容+上下文）
            search_text = chunk['content']
            if chunk['metadata'].get('title'):
                search_text = f"{chunk['metadata']['title']}\n{search_text}"

            ids.append(chunk_id)
            embeddings.append(self._get_embedding(search_text))
            documents.append(chunk['content'])
            metadatas.append(chunk['metadata'])

        # 批量添加到 ChromaDB
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

        return len(validated_chunks)

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.3
    ) -> List[Dict]:
        """
        语义搜索相关文档块

        Args:
            query: 查询文本
            top_k: 返回结果数量
            min_score: 最小相似度阈值

        Returns:
            相关文档块列表，按相似度排序
        """
        if not query.strip():
            return []

        # 获取查询向量
        query_embedding = self._get_embedding(query)

        # 执行搜索
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=['documents', 'metadatas', 'distances']
        )

        # 组装结果
        search_results = []

        if results['ids'] and results['ids'][0]:
            for i, doc_id in enumerate(results['ids'][0]):
                distance = results['distances'][0][i]
                similarity = 1 - distance  # 转换为相似度

                if similarity >= min_score:
                    search_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'similarity': similarity,
                        'distance': distance
                    })

        return search_results

    def get_stats(self) -> Dict:
        """
        获取向量存储统计信息

        Returns:
            统计信息字典
        """
        count = self.collection.count()
        return {
            'total_chunks': count,
            'collection_name': self.collection.name,
            'db_path': str(self.db_path)
        }

    def clear_all(self) -> bool:
        """
        清空所有数据

        Returns:
            是否成功清空
        """
        try:
            # 删除集合
            self.client.delete_collection(name=self.collection.name)
            # 重新创建空集合
            self.collection = self.client.get_or_create_collection(
                name="notes",
                metadata={"description": "用户笔记向量化存储"}
            )
            return True
        except Exception as e:
            print(f"清空向量数据库失败: {e}")
            return False

    def rebuild_from_chunks(self, chunks: List[Chunk]) -> int:
        """
        重建向量数据库（清空后重新添加）

        Args:
            chunks: 新的文档块列表

        Returns:
            成功添加的数量
        """
        self.clear_all()
        return self.add_chunks(chunks)


def create_vector_store(db_path: str = "./vector_db") -> VectorStore:
    """
    创建向量存储实例

    Args:
        db_path: 数据库路径

    Returns:
        VectorStore 实例
    """
    return VectorStore(db_path)


# 便捷函数
def search_notes(
    query: str,
    db_path: str = "./vector_db",
    top_k: int = 5,
    min_score: float = 0.3
) -> List[Dict]:
    """
    便捷的笔记搜索函数

    Args:
        query: 搜索查询
        db_path: 数据库路径
        top_k: 返回结果数量
        min_score: 最小相似度

    Returns:
        搜索结果列表
    """
    store = create_vector_store(db_path)
    return store.search(query, top_k, min_score)
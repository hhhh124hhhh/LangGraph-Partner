"""
知识检索相关API路由
提供向量存储、语义搜索、知识管理等功能
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse

from app.models.response import SuccessResponse, ErrorResponse, PaginatedResponse
from app.core.exceptions import ValidationError, VectorStoreError, NotFoundError
from app.core.security import InputValidator, rate_limit_dependency, is_safe_filename

router = APIRouter()


class KnowledgeSearchRequest(BaseModel):
    """知识搜索请求"""
    query: str = Field(..., description="搜索查询")
    top_k: int = Field(default=5, ge=1, le=20, description="返回结果数量")
    min_score: float = Field(default=0.3, ge=0.0, le=1.0, description="最小相似度阈值")
    filters: Optional[Dict[str, Any]] = Field(None, description="过滤条件")
    include_metadata: bool = Field(default=True, description="是否包含元数据")


class KnowledgeDocument(BaseModel):
    """知识文档模型"""
    doc_id: str = Field(..., description="文档ID")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    file_path: Optional[str] = Field(None, description="文件路径")
    file_type: str = Field(..., description="文件类型")
    chunk_count: int = Field(default=1, description="分块数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    tags: List[str] = Field(default_factory=list, description="标签")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")


class SearchResult(BaseModel):
    """搜索结果模型"""
    chunk_id: str = Field(..., description="文档块ID")
    doc_id: str = Field(..., description="文档ID")
    content: str = Field(..., description="内容片段")
    metadata: Dict[str, Any] = Field(..., description="元数据")
    similarity: float = Field(..., description="相似度分数")
    distance: float = Field(..., description="距离分数")
    highlights: List[str] = Field(default_factory=list, description="高亮片段")


class VectorStoreStats(BaseModel):
    """向量存储统计"""
    total_documents: int = Field(..., description="总文档数")
    total_chunks: int = Field(..., description="总块数")
    collection_size_mb: float = Field(..., description="集合大小（MB）")
    index_status: str = Field(..., description="索引状态")
    last_updated: datetime = Field(..., description="最后更新时间")
    embedding_model: str = Field(..., description="嵌入模型")


@router.get("/stats", summary="获取知识库统计")
async def get_knowledge_stats(_: None = Depends(rate_limit_dependency)):
    """
    获取知识库的统计信息

    Returns:
        知识库统计数据
    """
    try:
        # TODO: 从实际的向量存储获取统计信息
        # 这里暂时返回模拟数据
        stats = VectorStoreStats(
            total_documents=156,
            total_chunks=1248,
            collection_size_mb=45.7,
            index_status="ready",
            last_updated=datetime.now(),
            embedding_model="BAAI/bge-m3"
        )

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=stats, message="获取知识库统计成功")

    except Exception as e:
        raise VectorStoreError("获取知识库统计失败", "stats", {"error": str(e)})


@router.post("/search", summary="语义搜索")
async def search_knowledge(
    request: KnowledgeSearchRequest,
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

        # TODO: 使用实际的向量存储进行搜索
        # 这里暂时返回模拟搜索结果
        mock_results = [
            SearchResult(
                chunk_id=f"chunk_{i}_{hash(f'chunk_{i}') % 10000}",
                doc_id=f"doc_{i}",
                content=f"关于'{validated_query}'的相关内容片段 {i}。这里包含了详细的技术说明和示例代码。",
                metadata={
                    "title": f"技术文档 {i}",
                    "source": "knowledge_base.pdf",
                    "page": i + 1,
                    "chapter": f"第{i+1}章",
                    "tags": ["技术", "教程"]
                },
                similarity=0.95 - (i * 0.08),
                distance=0.05 + (i * 0.08),
                highlights=[f"<mark>{validated_query}</mark>的相关内容", f"重要的{validated_query}概念"]
            )
            for i in range(min(request.top_k, 8))
        ]

        # 过滤相似度
        filtered_results = [
            result for result in mock_results
            if result.similarity >= request.min_score
        ]

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=filtered_results, message="搜索成功")

    except ValueError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise VectorStoreError("语义搜索失败", "search", {"error": str(e)})


@router.get("/documents", response_model=PaginatedResponse, summary="获取文档列表")
async def list_documents(
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页大小"),
    file_type: Optional[str] = Query(None, description="文件类型过滤"),
    tag: Optional[str] = Query(None, description="标签过滤"),
    _: None = Depends(rate_limit_dependency)
):
    """
    获取知识库文档列表

    Args:
        page: 页码
        page_size: 每页大小
        file_type: 文件类型过滤
        tag: 标签过滤

    Returns:
        文档列表
    """
    try:
        # TODO: 从实际的向量存储获取文档列表
        # 这里暂时返回模拟文档数据
        mock_documents = [
            KnowledgeDocument(
                doc_id=f"doc_{i}_{hash(f'doc_{i}') % 10000}",
                title=f"技术文档 {i}",
                content=f"这是第{i}篇技术文档的内容摘要...",
                file_path=f"/knowledge/doc_{i}.pdf",
                file_type=["pdf", "md", "txt"][i % 3],
                chunk_count=8 + i,
                created_at=datetime.now() - timedelta(days=i),
                updated_at=datetime.now() - timedelta(hours=i),
                tags=[f"标签{i}", "技术", "教程"],
                metadata={"author": f"作者{i}", "version": f"1.{i}"}
            )
            for i in range(min(page_size, 15))
        ]

        # 应用过滤
        if file_type:
            mock_documents = [d for d in mock_documents if d.file_type == file_type]
        if tag:
            mock_documents = [d for d in mock_documents if tag in d.tags]

        total = 100  # 模拟总文档数

        from app.models.response import ResponseBuilder
        return ResponseBuilder.paginated(
            data=mock_documents,
            total=total,
            page=page,
            page_size=page_size,
            message="获取文档列表成功"
        )

    except Exception as e:
        raise VectorStoreError("获取文档列表失败", "list_documents", {"error": str(e)})


@router.get("/documents/{doc_id}", summary="获取文档详情")
async def get_document(
    doc_id: str,
    _: None = Depends(rate_limit_dependency)
):
    """
    获取指定文档的详细信息

    Args:
        doc_id: 文档ID

    Returns:
        文档详细信息
    """
    try:
        # TODO: 从实际的向量存储获取文档详情
        # 这里暂时返回模拟文档详情
        document = KnowledgeDocument(
            doc_id=doc_id,
            title="示例技术文档",
            content="这是完整的文档内容，包含了详细的技术说明、代码示例和最佳实践...",
            file_path="/knowledge/example.pdf",
            file_type="pdf",
            chunk_count=12,
            created_at=datetime.now() - timedelta(days=5),
            updated_at=datetime.now() - timedelta(hours=2),
            tags=["技术", "教程", "Python"],
            metadata={
                "author": "技术专家",
                "version": "2.0",
                "language": "中文",
                "word_count": 5000
            }
        )

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=document, message="获取文档详情成功")

    except Exception as e:
        raise NotFoundError("文档", doc_id)


@router.post("/upload", response_model=SuccessResponse, summary="上传文档")
async def upload_document(
    file: UploadFile = File(...),
    title: Optional[str] = None,
    tags: Optional[str] = None,
    chunk_size: int = Query(default=1000, ge=100, le=5000, description="分块大小"),
    _: None = Depends(rate_limit_dependency)
):
    """
    上传文档到知识库

    Args:
        file: 上传的文件
        title: 文档标题
        tags: 文档标签（逗号分隔）
        chunk_size: 分块大小

    Returns:
        上传结果
    """
    try:
        # 验证文件名安全性
        if not is_safe_filename(file.filename):
            raise ValidationError("文件名不安全")

        # 验证文件类型
        allowed_types = ["text/plain", "text/markdown", "application/pdf", "text/html"]
        if file.content_type not in allowed_types:
            raise ValidationError(f"不支持的文件类型: {file.content_type}")

        # 验证文件大小（10MB限制）
        file_size = 0
        content = await file.read()
        file_size = len(content)
        await file.seek(0)  # 重置文件指针

        if file_size > 10 * 1024 * 1024:  # 10MB
            raise ValidationError("文件大小超过10MB限制")

        # TODO: 实际的文档处理和向量化逻辑
        doc_id = f"doc_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(file.filename) % 10000}"
        chunk_count = max(1, file_size // chunk_size)

        # 处理标签
        tag_list = []
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

        return SuccessResponse(
            success=True,
            message="文档上传成功",
            data={
                "doc_id": doc_id,
                "filename": file.filename,
                "title": title or file.filename,
                "file_size": file_size,
                "chunk_count": chunk_count,
                "tags": tag_list,
                "processing_status": "queued"
            }
        )

    except ValidationError:
        raise
    except Exception as e:
        raise VectorStoreError("文档上传失败", "upload", {"error": str(e)})


@router.delete("/documents/{doc_id}", response_model=SuccessResponse, summary="删除文档")
async def delete_document(
    doc_id: str,
    confirm: bool = Query(default=False, description="确认删除"),
    _: None = Depends(rate_limit_dependency)
):
    """
    删除指定的文档

    Args:
        doc_id: 文档ID
        confirm: 是否确认删除

    Returns:
        删除结果
    """
    try:
        if not confirm:
            raise ValidationError("请确认删除操作")

        # TODO: 实际的文档删除逻辑
        # 这里暂时返回成功响应

        return SuccessResponse(
            success=True,
            message=f"文档 {doc_id} 已删除",
            data={
                "doc_id": doc_id,
                "deleted_chunks": 15
            }
        )

    except ValidationError:
        raise
    except Exception as e:
        raise VectorStoreError("删除文档失败", "delete", {"error": str(e)})


@router.post("/rebuild", response_model=SuccessResponse, summary="重建索引")
async def rebuild_index(
    confirm: bool = Query(default=False, description="确认重建"),
    _: None = Depends(rate_limit_dependency)
):
    """
    重建向量存储索引

    Args:
        confirm: 是否确认重建

    Returns:
        重建结果
    """
    try:
        if not confirm:
            raise ValidationError("请确认重建索引操作")

        # TODO: 实际的索引重建逻辑
        # 这里暂时返回模拟结果

        return SuccessResponse(
            success=True,
            message="向量索引重建成功",
            data={
                "total_documents": 156,
                "total_chunks": 1248,
                "processing_time": 45.2,
                "index_size_mb": 45.7,
                "embedding_model": "BAAI/bge-m3"
            }
        )

    except ValidationError:
        raise
    except Exception as e:
        raise VectorStoreError("重建索引失败", "rebuild", {"error": str(e)})


@router.get("/similar/{doc_id}", response_model=List[Dict[str, Any]], summary="查找相似文档")
async def find_similar_documents(
    doc_id: str,
    top_k: int = Query(default=5, ge=1, le=20, description="返回数量"),
    min_score: float = Query(default=0.5, ge=0.0, le=1.0, description="最小相似度"),
    _: None = Depends(rate_limit_dependency)
):
    """
    查找与指定文档相似的文档

    Args:
        doc_id: 文档ID
        top_k: 返回数量
        min_score: 最小相似度

    Returns:
        相似文档列表
    """
    try:
        # TODO: 实际的相似文档查找逻辑
        # 这里暂时返回模拟结果
        similar_docs = [
            {
                "doc_id": f"similar_doc_{i}",
                "title": f"相似文档 {i}",
                "similarity": 0.9 - (i * 0.1),
                "shared_tags": [f"标签{i}", "共同标签"],
                "content_preview": f"与原文档相似的预览内容 {i}..."
            }
            for i in range(min(top_k, 8))
            if 0.9 - (i * 0.1) >= min_score
        ]

        return similar_docs

    except Exception as e:
        raise VectorStoreError("查找相似文档失败", "find_similar", {"error": str(e)})


@router.get("/tags", summary="获取标签统计")
async def get_tag_stats(_: None = Depends(rate_limit_dependency)):
    """
    获取知识库标签统计信息

    Returns:
        标签统计数据
    """
    try:
        # TODO: 实际的标签统计逻辑
        # 这里暂时返回模拟数据
        tag_stats = {
            "total_tags": 45,
            "most_used_tags": [
                {"tag": "Python", "count": 28},
                {"tag": "机器学习", "count": 19},
                {"tag": "FastAPI", "count": 15},
                {"tag": "LangGraph", "count": 12},
                {"tag": "教程", "count": 10}
            ],
            "tag_distribution": {
                "技术": 156,
                "教程": 89,
                "工具": 67,
                "最佳实践": 45,
                "案例研究": 23
            },
            "recent_tags": ["LangGraph", "向量数据库", "RAG", "AI助手", "FastAPI"]
        }

        from app.models.response import ResponseBuilder
        return ResponseBuilder.success(data=tag_stats, message="获取标签统计成功")

    except Exception as e:
        raise VectorStoreError("获取标签统计失败", "tag_stats", {"error": str(e)})

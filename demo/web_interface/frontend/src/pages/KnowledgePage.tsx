/**
 * 知识库管理页面
 * 提供完整的知识库管理功能，包括统计、搜索、文档管理、上传等
 */

import React, { useState, useCallback } from 'react';
import {
  useKnowledgeStatsQuery,
  useKnowledgeDocumentsQuery,
  useKnowledgeTagsQuery,
  useKnowledgeDocumentQuery,
  useSimilarDocumentsQuery,
  useDocumentUploadMutation,
  useDocumentDeleteMutation,
  useRebuildIndexMutation,
  useKnowledgeSearchMutation,
} from '@hooks/useApiQuery';
import {
  KnowledgeStats,
  KnowledgeDocument,
  TagStats,
  DocumentUploadRequest,
  SimilarDocument,
} from '@typesdef/index';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { cn, formatDateTime, formatFileSize, truncateText } from '@utils/index';

// 组件导入
import StatsDashboard from './components/StatsDashboard';
import DocumentGrid from './components/DocumentGrid';
import SearchBar from './components/SearchBar';
import UploadModal from './components/UploadModal';
import DocumentDetailModal from './components/DocumentDetailModal';
import TagCloud from './components/TagCloud';
import FilterPanel from './components/FilterPanel';

const KnowledgePage: React.FC = () => {
  // 页面状态管理
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [selectedDocument, setSelectedDocument] = useState<KnowledgeDocument | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [showDocumentDetail, setShowDocumentDetail] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  const pageSize = 12;

  // API查询
  const { data: stats, isLoading: statsLoading, error: statsError } = useKnowledgeStatsQuery();

  const {
    data: documentsData,
    isLoading: documentsLoading,
    error: documentsError
  } = useKnowledgeDocumentsQuery({
    page: currentPage,
    page_size: pageSize,
    tags: selectedTags.length > 0 ? selectedTags : undefined,
    category: selectedCategory || undefined,
    sort_by: 'updated_at',
    sort_order: 'desc',
  });

  const { data: tags, isLoading: tagsLoading } = useKnowledgeTagsQuery();

  const { data: documentDetail } = useKnowledgeDocumentQuery(
    selectedDocument?.id || '',
    !!selectedDocument?.id
  );

  const { data: similarDocuments } = useSimilarDocumentsQuery(
    selectedDocument?.id || '',
    5,
    !!selectedDocument?.id
  );

  // API变更
  const uploadMutation = useDocumentUploadMutation();
  const deleteMutation = useDocumentDeleteMutation();
  const rebuildMutation = useRebuildIndexMutation();
  const searchMutation = useKnowledgeSearchMutation();

  // 事件处理
  const handleSearch = useCallback(async (query: string) => {
    if (!query.trim()) return;

    try {
      await searchMutation.mutateAsync({
        query: query.trim(),
        limit: pageSize,
        filters: {
          tags: selectedTags.length > 0 ? selectedTags : undefined,
          category: selectedCategory || undefined,
        },
      });
    } catch (error) {
      console.error('搜索失败:', error);
    }
  }, [selectedTags, selectedCategory, searchMutation]);

  const handleDocumentClick = useCallback((document: KnowledgeDocument) => {
    setSelectedDocument(document);
    setShowDocumentDetail(true);
  }, []);

  const handleDocumentDelete = useCallback(async (documentId: string) => {
    if (!confirm('确定要删除这个文档吗？此操作不可撤销。')) return;

    try {
      await deleteMutation.mutateAsync(documentId);
      setShowDocumentDetail(false);
      setSelectedDocument(null);
    } catch (error) {
      console.error('删除文档失败:', error);
    }
  }, [deleteMutation]);

  const handleFileUpload = useCallback(async (request: DocumentUploadRequest, onProgress?: (progress: number) => void) => {
    try {
      await uploadMutation.mutateAsync({ request, onProgress });
      setShowUploadModal(false);
    } catch (error) {
      console.error('上传文档失败:', error);
    }
  }, [uploadMutation]);

  const handleRebuildIndex = useCallback(async () => {
    if (!confirm('确定要重建索引吗？这可能需要一些时间。')) return;

    try {
      await rebuildMutation.mutateAsync();
    } catch (error) {
      console.error('重建索引失败:', error);
    }
  }, [rebuildMutation]);

  const handleTagSelect = useCallback((tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
    setCurrentPage(1);
  }, []);

  const handleCategorySelect = useCallback((category: string) => {
    setSelectedCategory(prev =>
      prev === category ? '' : category
    );
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  const clearFilters = useCallback(() => {
    setSelectedTags([]);
    setSelectedCategory('');
    setSearchQuery('');
    setCurrentPage(1);
  }, []);

  // 计算派生状态
  const documents = documentsData?.documents || [];
  const totalDocuments = documentsData?.total || 0;
  const totalPages = documentsData?.total_pages || 1;
  const hasActiveFilters = selectedTags.length > 0 || selectedCategory !== '';

  // 渲染统计仪表板
  const renderStatsDashboard = () => {
    if (statsError) {
      return (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
          <p className="text-red-700 dark:text-red-300">加载统计数据失败</p>
        </div>
      );
    }

    return (
      <StatsDashboard
        stats={stats}
        loading={statsLoading}
        onRebuildIndex={handleRebuildIndex}
        rebuildLoading={rebuildMutation.isLoading}
      />
    );
  };

  // 渲染文档列表
  const renderDocuments = () => {
    if (documentsError) {
      return (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-8 text-center">
          <p className="text-red-700 dark:text-red-300 mb-4">加载文档列表失败</p>
          <Button onClick={() => window.location.reload()}>重新加载</Button>
        </div>
      );
    }

    if (documents.length === 0 && !documentsLoading) {
      return (
        <div className="bg-gray-50 dark:bg-gray-800/50 border border-gray-200 dark:border-gray-700 rounded-lg p-8 text-center">
          <div className="text-gray-400 mb-4">
            <svg className="w-16 h-16 mx-auto mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
            {hasActiveFilters ? '没有找到匹配的文档' : '还没有任何文档'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400 mb-4">
            {hasActiveFilters ? '尝试调整过滤条件' : '上传一些文档来开始构建您的知识库'}
          </p>
          <div className="flex gap-2 justify-center">
            {hasActiveFilters && (
              <Button variant="outline" onClick={clearFilters}>
                清除过滤条件
              </Button>
            )}
            <Button onClick={() => setShowUploadModal(true)}>
              上传文档
            </Button>
          </div>
        </div>
      );
    }

    return (
      <DocumentGrid
        documents={documents}
        loading={documentsLoading}
        viewMode={viewMode}
        onDocumentClick={handleDocumentClick}
        onDocumentDelete={handleDocumentDelete}
        onDeleteLoading={deleteMutation.isLoading}
      />
    );
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* 页面头部 */}
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              📚 知识库
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              管理您的文档和知识内容，支持智能搜索和语义检索
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              onClick={() => setViewMode(viewMode === 'grid' ? 'list' : 'grid')}
            >
              {viewMode === 'grid' ? '📋' : '⊞'}
            </Button>
            <Button onClick={() => setShowUploadModal(true)}>
              📤 上传文档
            </Button>
          </div>
        </div>
      </div>

      {/* 统计仪表板 */}
      <div className="mb-8">
        {renderStatsDashboard()}
      </div>

      {/* 搜索和过滤 */}
      <div className="mb-6">
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
          onSearch={handleSearch}
          loading={searchMutation.isLoading}
          placeholder="搜索文档内容..."
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* 侧边栏过滤 */}
        <div className="lg:col-span-1">
          <div className="space-y-6">
            {/* 标签云 */}
            <TagCloud
              tags={tags || []}
              selectedTags={selectedTags}
              onTagSelect={handleTagSelect}
              loading={tagsLoading}
            />

            {/* 过滤面板 */}
            <FilterPanel
              selectedCategory={selectedCategory}
              onCategorySelect={handleCategorySelect}
              onClearFilters={clearFilters}
              hasActiveFilters={hasActiveFilters}
              categories={stats?.document_types ? Object.keys(stats.document_types) : []}
            />
          </div>
        </div>

        {/* 主内容区域 */}
        <div className="lg:col-span-3">
          {/* 文档列表 */}
          <div className="mb-6">
            {renderDocuments()}
          </div>

          {/* 分页 */}
          {totalPages > 1 && (
            <div className="flex justify-center">
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                >
                  上一页
                </Button>

                <span className="text-sm text-gray-600 dark:text-gray-400">
                  第 {currentPage} 页，共 {totalPages} 页 ({totalDocuments} 个文档)
                </span>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                >
                  下一页
                </Button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 上传模态框 */}
      {showUploadModal && (
        <UploadModal
          onClose={() => setShowUploadModal(false)}
          onUpload={handleFileUpload}
          loading={uploadMutation.isLoading}
        />
      )}

      {/* 文档详情模态框 */}
      {showDocumentDetail && selectedDocument && (
        <DocumentDetailModal
          document={documentDetail || selectedDocument}
          similarDocuments={similarDocuments || []}
          loading={!documentDetail}
          onClose={() => {
            setShowDocumentDetail(false);
            setSelectedDocument(null);
          }}
          onDelete={() => handleDocumentDelete(selectedDocument.id)}
          deleteLoading={deleteMutation.isLoading}
        />
      )}
    </div>
  );
};

export default KnowledgePage;
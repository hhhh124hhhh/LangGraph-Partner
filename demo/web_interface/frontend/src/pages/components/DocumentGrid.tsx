/**
 * 文档网格组件
 */

import React from 'react';
import { KnowledgeDocument } from '@typesdef/index';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { formatDateTime, formatFileSize, truncateText } from '@utils/index';

interface DocumentGridProps {
  documents: KnowledgeDocument[];
  loading: boolean;
  viewMode: 'grid' | 'list';
  onDocumentClick: (document: KnowledgeDocument) => void;
  onDocumentDelete: (documentId: string) => void;
  onDeleteLoading: boolean;
}

const DocumentGrid: React.FC<DocumentGridProps> = ({
  documents,
  loading,
  viewMode,
  onDocumentClick,
  onDocumentDelete,
  onDeleteLoading,
}) => {
  const getDocumentIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'md':
      case 'markdown':
        return '📝';
      case 'pdf':
        return '📕';
      case 'doc':
      case 'docx':
        return '📘';
      case 'txt':
        return '📄';
      default:
        return '📄';
    }
  };

  const DocumentCard: React.FC<{ document: KnowledgeDocument }> = ({ document }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow cursor-pointer">
      <div className="p-6">
        {/* 文档头部 */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center flex-1 min-w-0">
            <div className="text-2xl mr-3 flex-shrink-0">
              {getDocumentIcon(document.file_path)}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                {document.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate">
                {document.file_path.split('/').pop()}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1 ml-2 flex-shrink-0">
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDocumentClick(document);
              }}
              title="查看详情"
            >
              👁️
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={(e) => {
                e.stopPropagation();
                onDocumentDelete(document.id);
              }}
              disabled={onDeleteLoading}
              title="删除文档"
            >
              🗑️
            </Button>
          </div>
        </div>

        {/* 文档描述 */}
        {document.metadata?.description && (
          <p className="text-sm text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">
            {truncateText(document.metadata.description, 100)}
          </p>
        )}

        {/* 标签 */}
        {document.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {document.tags.slice(0, 3).map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
              >
                {tag}
              </span>
            ))}
            {document.tags.length > 3 && (
              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                +{document.tags.length - 3}
              </span>
            )}
          </div>
        )}

        {/* 文档元信息 */}
        <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
          <div className="flex items-center gap-4">
            <span>📊 {document.metadata?.word_count || 0} 字</span>
            <span>💾 {formatFileSize(document.file_size)}</span>
          </div>
          <span title={formatDateTime(document.updated_at)}>
            {formatDateTime(document.updated_at, 'MM-DD')}
          </span>
        </div>

        {/* 相似度评分（如果有） */}
        {document.similarity_score !== undefined && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-500 dark:text-gray-400">相关度</span>
              <div className="flex items-center">
                <div className="w-20 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${Math.round(document.similarity_score * 100)}%` }}
                  ></div>
                </div>
                <span className="text-xs font-medium text-gray-900 dark:text-white">
                  {Math.round(document.similarity_score * 100)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  const DocumentListItem: React.FC<{ document: KnowledgeDocument }> = ({ document }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center flex-1 min-w-0">
            <div className="text-2xl mr-4 flex-shrink-0">
              {getDocumentIcon(document.file_path)}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                {document.title}
              </h3>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate mb-2">
                {document.file_path.split('/').pop()}
              </p>
              {document.metadata?.description && (
                <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-1 mb-2">
                  {truncateText(document.metadata.description, 120)}
                </p>
              )}
              <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                <span>📊 {document.metadata?.word_count || 0} 字</span>
                <span>💾 {formatFileSize(document.file_size)}</span>
                <span>🕒 {formatDateTime(document.updated_at, 'MM-DD HH:mm')}</span>
              </div>
              {document.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {document.tags.slice(0, 5).map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                    >
                      {tag}
                    </span>
                  ))}
                  {document.tags.length > 5 && (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                      +{document.tags.length - 5}
                    </span>
                  )}
                </div>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2 ml-4 flex-shrink-0">
            {document.similarity_score !== undefined && (
              <div className="text-right mr-2">
                <div className="text-xs text-gray-500 dark:text-gray-400">相关度</div>
                <div className="text-sm font-medium text-gray-900 dark:text-white">
                  {Math.round(document.similarity_score * 100)}%
                </div>
              </div>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDocumentClick(document)}
            >
              查看详情
            </Button>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onDocumentDelete(document.id)}
              disabled={onDeleteLoading}
            >
              🗑️
            </Button>
          </div>
        </div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
        {[...Array(6)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="animate-pulse">
              <div className="flex items-center mb-4">
                <div className="w-8 h-8 bg-gray-300 dark:bg-gray-600 rounded mr-3"></div>
                <div className="flex-1">
                  <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
                  <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
                </div>
              </div>
              <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
              <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-5/6"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return null; // 由父组件处理空状态
  }

  return (
    <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4' : 'space-y-4'}>
      {documents.map((document) => (
        <div key={document.id} onClick={() => onDocumentClick(document)}>
          {viewMode === 'grid' ? (
            <DocumentCard document={document} />
          ) : (
            <DocumentListItem document={document} />
          )}
        </div>
      ))}
    </div>
  );
};

export default DocumentGrid;
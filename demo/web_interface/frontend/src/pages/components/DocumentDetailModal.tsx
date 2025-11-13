/**
 * 文档详情模态框组件
 */

import React, { useState } from 'react';
import { KnowledgeDocument, SimilarDocument } from '@typesdef/index';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { formatDateTime, formatFileSize, truncateText } from '@utils/index';

interface DocumentDetailModalProps {
  document: KnowledgeDocument;
  similarDocuments: SimilarDocument[];
  loading: boolean;
  onClose: () => void;
  onDelete: () => void;
  deleteLoading: boolean;
}

const DocumentDetailModal: React.FC<DocumentDetailModalProps> = ({
  document,
  similarDocuments,
  loading,
  onClose,
  onDelete,
  deleteLoading,
}) => {
  const [activeTab, setActiveTab] = useState<'content' | 'metadata' | 'similar'>('content');

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

  const renderContentTab = () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">文档内容</h3>
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 max-h-96 overflow-y-auto">
          <pre className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap font-mono">
            {loading ? <LoadingSpinner /> : document.content}
          </pre>
        </div>
      </div>

      {/* 文档统计 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {document.metadata?.word_count || 0}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">字数</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {document.metadata?.chunk_count || 0}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">文本块</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {document.tags.length}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">标签</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
            {formatFileSize(document.file_size)}
          </div>
          <div className="text-sm text-gray-600 dark:text-gray-400">文件大小</div>
        </div>
      </div>
    </div>
  );

  const renderMetadataTab = () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">文档信息</h3>
        <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
          <dl className="space-y-3">
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">文件名</dt>
              <dd className="text-sm text-gray-900 dark:text-white">
                {document.file_path.split('/').pop()}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">文件路径</dt>
              <dd className="text-sm text-gray-900 dark:text-white truncate ml-2">
                {document.file_path}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">创建时间</dt>
              <dd className="text-sm text-gray-900 dark:text-white">
                {formatDateTime(document.created_at)}
              </dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">更新时间</dt>
              <dd className="text-sm text-gray-900 dark:text-white">
                {formatDateTime(document.updated_at)}
              </dd>
            </div>
            {document.metadata?.author && (
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">作者</dt>
                <dd className="text-sm text-gray-900 dark:text-white">
                  {document.metadata.author}
                </dd>
              </div>
            )}
            {document.metadata?.category && (
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">分类</dt>
                <dd className="text-sm text-gray-900 dark:text-white">
                  {document.metadata.category}
                </dd>
              </div>
            )}
            {document.metadata?.language && (
              <div className="flex justify-between">
                <dt className="text-sm font-medium text-gray-600 dark:text-gray-400">语言</dt>
                <dd className="text-sm text-gray-900 dark:text-white">
                  {document.metadata.language}
                </dd>
              </div>
            )}
          </dl>
        </div>
      </div>

      {/* 标签 */}
      {document.tags.length > 0 && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">标签</h3>
          <div className="flex flex-wrap gap-2">
            {document.tags.map((tag) => (
              <span
                key={tag}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
              >
                {tag}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* 描述 */}
      {document.metadata?.description && (
        <div>
          <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">描述</h3>
          <div className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4">
            <p className="text-sm text-gray-700 dark:text-gray-300">
              {document.metadata.description}
            </p>
          </div>
        </div>
      )}
    </div>
  );

  const renderSimilarTab = () => (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">相似文档</h3>
        {similarDocuments.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            没有找到相似的文档
          </div>
        ) : (
          <div className="space-y-3">
            {similarDocuments.map((similar, index) => (
              <div
                key={similar.document.id}
                className="bg-gray-50 dark:bg-gray-900/50 rounded-lg p-4 hover:bg-gray-100 dark:hover:bg-gray-900/70 transition-colors cursor-pointer"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                      {similar.document.title}
                    </h4>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {similar.document.file_path.split('/').pop()}
                    </p>
                  </div>
                  <div className="ml-3 flex-shrink-0">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${Math.round(similar.similarity_score * 100)}%` }}
                        ></div>
                      </div>
                      <span className="text-xs font-medium text-gray-900 dark:text-white">
                        {Math.round(similar.similarity_score * 100)}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* 相似度详情 */}
                <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
                  <span>📊 {similar.document.metadata?.word_count || 0} 字</span>
                  <span>💾 {formatFileSize(similar.document.file_size)}</span>
                  {similar.shared_tags.length > 0 && (
                    <span>🏷️ 共享标签: {similar.shared_tags.slice(0, 3).join(', ')}</span>
                  )}
                </div>

                {/* 共享标签 */}
                {similar.shared_tags.length > 0 && (
                  <div className="mt-2 flex flex-wrap gap-1">
                    {similar.shared_tags.slice(0, 5).map((tag) => (
                      <span
                        key={tag}
                        className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200"
                      >
                        {tag}
                      </span>
                    ))}
                    {similar.shared_tags.length > 5 && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400">
                        +{similar.shared_tags.length - 5}
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-4xl mx-4 max-h-[90vh] overflow-hidden">
        {/* 头部 */}
        <div className="flex items-start justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-start space-x-3 flex-1 min-w-0">
            <div className="text-3xl flex-shrink-0">
              {getDocumentIcon(document.file_path)}
            </div>
            <div className="flex-1 min-w-0">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white truncate">
                {document.title}
              </h2>
              <p className="text-sm text-gray-500 dark:text-gray-400 truncate mt-1">
                {document.file_path}
              </p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            ✕
          </Button>
        </div>

        {/* 标签页导航 */}
        <div className="border-b border-gray-200 dark:border-gray-700">
          <nav className="flex space-x-8 px-6">
            <button
              className={`
                py-3 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'content'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }
              `}
              onClick={() => setActiveTab('content')}
            >
              📄 内容
            </button>
            <button
              className={`
                py-3 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'metadata'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }
              `}
              onClick={() => setActiveTab('metadata')}
            >
              ℹ️ 信息
            </button>
            <button
              className={`
                py-3 px-1 border-b-2 font-medium text-sm
                ${activeTab === 'similar'
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                }
              `}
              onClick={() => setActiveTab('similar')}
            >
              🔗 相似文档 ({similarDocuments.length})
            </button>
          </nav>
        </div>

        {/* 内容区域 */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'content' && renderContentTab()}
          {activeTab === 'metadata' && renderMetadataTab()}
          {activeTab === 'similar' && renderSimilarTab()}
        </div>

        {/* 底部按钮 */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="danger"
            onClick={onDelete}
            loading={deleteLoading}
            disabled={loading}
          >
            删除文档
          </Button>
          <Button variant="outline" onClick={onClose}>
            关闭
          </Button>
        </div>
      </div>
    </div>
  );
};

export default DocumentDetailModal;
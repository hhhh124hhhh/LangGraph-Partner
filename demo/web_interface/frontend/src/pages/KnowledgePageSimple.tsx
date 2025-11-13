import React, { useState } from 'react';
import {
  Database,
  Search,
  Upload,
  Filter,
  Grid,
  List,
  Plus,
  FileText,
  Tag,
  Calendar,
  BarChart3
} from 'lucide-react';
import { useAppStore } from '@stores/index';
import { cn } from '@utils/index';
import Button from '@components/Button';

const KnowledgePage: React.FC = () => {
  const { theme } = useAppStore();
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // 模拟数据
  const stats = {
    total_documents: 42,
    total_chunks: 256,
    total_tags: 18,
    storage_size: 2.4,
    last_updated: '2025-11-13'
  };

  const documents = [
    {
      doc_id: '1',
      title: '项目笔记 - LangGraph实践',
      content: '这是一个关于LangGraph实践项目的详细笔记...',
      file_type: 'markdown',
      chunk_count: 8,
      created_at: '2025-11-10',
      tags: ['技术', 'LangGraph', '笔记']
    },
    {
      doc_id: '2',
      title: 'AI Partner使用指南',
      content: 'AI Partner的完整使用指南和最佳实践...',
      file_type: 'markdown',
      chunk_count: 12,
      created_at: '2025-11-08',
      tags: ['指南', 'AI', '使用方法']
    }
  ];

  const allTags = ['技术', 'LangGraph', '笔记', '指南', 'AI', '使用方法', '项目', '实践'];

  return (
    <div className="p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* 页面标题 */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <Database className="w-8 h-8 text-primary-600" />
              知识库
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">
              管理您的笔记和知识内容，支持智能搜索和语义检索
            </p>
          </div>
          <Button
            icon={<Plus className="w-4 h-4" />}
            onClick={() => console.log('上传文档')}
          >
            上传文档
          </Button>
        </div>

        {/* 统计卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">文档总数</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.total_documents}
                </p>
              </div>
              <FileText className="w-8 h-8 text-blue-600" />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">内容块数</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.total_chunks}
                </p>
              </div>
              <Database className="w-8 h-8 text-green-600" />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">标签数量</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.total_tags}
                </p>
              </div>
              <Tag className="w-8 h-8 text-purple-600" />
            </div>
          </div>

          <div className="card p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">存储空间</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">
                  {stats.storage_size}MB
                </p>
              </div>
              <BarChart3 className="w-8 h-8 text-orange-600" />
            </div>
          </div>
        </div>

        {/* 搜索和过滤栏 */}
        <div className="card p-4">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* 搜索框 */}
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <input
                  type="text"
                  placeholder="搜索知识库内容..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                />
              </div>
            </div>

            {/* 标签过滤 */}
            <div className="flex items-center gap-2">
              <Filter className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <div className="flex flex-wrap gap-2">
                {allTags.slice(0, 5).map(tag => (
                  <button
                    key={tag}
                    onClick={() => {
                      if (selectedTags.includes(tag)) {
                        setSelectedTags(selectedTags.filter(t => t !== tag));
                      } else {
                        setSelectedTags([...selectedTags, tag]);
                      }
                    }}
                    className={cn(
                      'px-3 py-1 rounded-full text-sm font-medium transition-colors',
                      selectedTags.includes(tag)
                        ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300'
                    )}
                  >
                    {tag}
                  </button>
                ))}
              </div>
            </div>

            {/* 视图切换 */}
            <div className="flex items-center gap-2 border border-gray-300 dark:border-gray-600 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'p-2 rounded transition-colors',
                  viewMode === 'grid'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-400'
                )}
              >
                <Grid className="w-4 h-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-2 rounded transition-colors',
                  viewMode === 'list'
                    ? 'bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
                    : 'text-gray-600 dark:text-gray-400'
                )}
              >
                <List className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {/* 文档列表 */}
        <div className="space-y-4">
          {documents.map(doc => (
            <div key={doc.doc_id} className="card p-6 hover:shadow-medium transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                    {doc.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                    {doc.content}
                  </p>
                  <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                    <span className="flex items-center gap-1">
                      <FileText className="w-4 h-4" />
                      {doc.file_type}
                    </span>
                    <span className="flex items-center gap-1">
                      <Database className="w-4 h-4" />
                      {doc.chunk_count} 块
                    </span>
                    <span className="flex items-center gap-1">
                      <Calendar className="w-4 h-4" />
                      {doc.created_at}
                    </span>
                  </div>
                  <div className="flex flex-wrap gap-2 mt-3">
                    {doc.tags.map(tag => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300
                                 rounded-md text-sm"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  <Button variant="outline" size="sm">
                    查看详情
                  </Button>
                  <Button variant="ghost" size="sm" className="text-red-600 hover:text-red-700">
                    删除
                  </Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* 空状态 */}
        {documents.length === 0 && (
          <div className="text-center py-16">
            <Database className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              暂无文档
            </h3>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              开始上传您的第一个文档，构建个人知识库
            </p>
            <Button icon={<Upload className="w-4 h-4" />}>
              上传文档
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default KnowledgePage;
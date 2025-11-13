/**
 * 知识库统计仪表板组件
 */

import React from 'react';
import { KnowledgeStats } from '@typesdef/index';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';
import { formatFileSize, formatDateTime } from '@utils/index';

interface StatsDashboardProps {
  stats: KnowledgeStats | null;
  loading: boolean;
  onRebuildIndex: () => void;
  rebuildLoading: boolean;
}

const StatsDashboard: React.FC<StatsDashboardProps> = ({
  stats,
  loading,
  onRebuildIndex,
  rebuildLoading,
}) => {
  const StatCard: React.FC<{
    title: string;
    value: string | number;
    icon: string;
    description?: string;
    trend?: 'up' | 'down' | 'stable';
  }> = ({ title, value, icon, description, trend }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <div className="text-2xl">{icon}</div>
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{title}</p>
          <p className="text-2xl font-semibold text-gray-900 dark:text-white">
            {loading ? <LoadingSpinner size="sm" /> : value}
          </p>
          {description && (
            <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">{description}</p>
          )}
        </div>
        {trend && (
          <div className="flex-shrink-0">
            {trend === 'up' && <span className="text-green-500">📈</span>}
            {trend === 'down' && <span className="text-red-500">📉</span>}
            {trend === 'stable' && <span className="text-gray-500">➡️</span>}
          </div>
        )}
      </div>
    </div>
  );

  if (loading && !stats) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
            <div className="animate-pulse">
              <div className="h-4 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
              <div className="h-8 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
              <div className="h-3 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
          📊 知识库统计
        </h2>
        <Button
          variant="outline"
          size="sm"
          onClick={onRebuildIndex}
          loading={rebuildLoading}
          disabled={loading}
        >
          🔄 重建索引
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard
          title="文档总数"
          value={stats?.total_documents || 0}
          icon="📄"
          description={`${stats?.total_chunks || 0} 个文本块`}
        />
        <StatCard
          title="标签数量"
          value={stats?.total_tags || 0}
          icon="🏷️"
          description="分类标签"
        />
        <StatCard
          title="存储空间"
          value={formatFileSize((stats?.storage_size_mb || 0) * 1024 * 1024)}
          icon="💾"
          description="磁盘占用"
        />
        <StatCard
          title="最后更新"
          value={stats?.last_updated ? formatDateTime(stats.last_updated, 'MM-DD HH:mm') : '未知'}
          icon="🕒"
          description="索引更新时间"
        />
      </div>

      {/* 文档类型分布 */}
      {stats?.document_types && Object.keys(stats.document_types).length > 0 && (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            📈 文档类型分布
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(stats.document_types).map(([type, count]) => (
              <div key={type} className="text-center">
                <div className="text-2xl font-bold text-primary-600 dark:text-primary-400">
                  {count}
                </div>
                <div className="text-sm text-gray-600 dark:text-gray-400 capitalize">
                  {type}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default StatsDashboard;
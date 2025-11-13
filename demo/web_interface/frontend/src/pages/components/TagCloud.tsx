/**
 * 标签云组件
 */

import React from 'react';
import { TagStats } from '@typesdef/index';
import LoadingSpinner from '@components/LoadingSpinner';
import { formatDateTime } from '@utils/index';

interface TagCloudProps {
  tags: TagStats[];
  selectedTags: string[];
  onTagSelect: (tag: string) => void;
  loading: boolean;
}

const TagCloud: React.FC<TagCloudProps> = ({
  tags = [],
  selectedTags = [],
  onTagSelect,
  loading,
}) => {
  // 确保 tags 是数组
  const safeTags = Array.isArray(tags) ? tags : [];

  if (loading && safeTags.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          🏷️ 标签云
        </h3>
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (safeTags.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          🏷️ 标签云
        </h3>
        <div className="text-center py-8 text-gray-500 dark:text-gray-400">
          暂无标签
        </div>
      </div>
    );
  }

  // 计算标签的权重（用于字体大小）
  const maxCount = Math.max(...safeTags.map(tag => tag.count));
  const minCount = Math.min(...safeTags.map(tag => tag.count));
  const range = maxCount - minCount || 1;

  const getTagSize = (count: number): string => {
    const normalized = (count - minCount) / range;
    if (normalized > 0.8) return 'text-lg font-bold';
    if (normalized > 0.6) return 'text-base font-semibold';
    if (normalized > 0.4) return 'text-sm font-medium';
    return 'text-xs';
  };

  const getTagColor = (count: number): string => {
    const normalized = (count - minCount) / range;
    if (normalized > 0.8) return 'text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20';
    if (normalized > 0.6) return 'text-indigo-600 dark:text-indigo-400 hover:bg-indigo-50 dark:hover:bg-indigo-900/20';
    if (normalized > 0.4) return 'text-purple-600 dark:text-purple-400 hover:bg-purple-50 dark:hover:bg-purple-900/20';
    return 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/50';
  };

  // 按使用频率排序标签
  const sortedTags = [...safeTags].sort((a, b) => b.count - a.count);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          🏷️ 标签云
        </h3>
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {safeTags.length} 个标签
        </span>
      </div>

      {/* 选中的标签 */}
      {selectedTags.length > 0 && (
        <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
          <div className="text-sm text-blue-800 dark:text-blue-200 mb-2">
            已选择的标签:
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedTags.map((tag) => (
              <button
                key={tag}
                onClick={() => onTagSelect(tag)}
                className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 hover:bg-blue-200 dark:hover:bg-blue-900/40 transition-colors"
              >
                {tag}
                <span className="hover:text-blue-900 dark:hover:text-blue-100">×</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 标签云 */}
      <div className="flex flex-wrap gap-2">
        {sortedTags.slice(0, 50).map((tag) => {
          const isSelected = selectedTags.includes(tag.tag);
          return (
            <button
              key={tag.tag}
              onClick={() => onTagSelect(tag.tag)}
              className={`
                inline-flex items-center px-2 py-1 rounded-full transition-all duration-200
                ${getTagSize(tag.count)}
                ${isSelected
                  ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200 ring-2 ring-blue-500'
                  : `${getTagColor(tag.count)} hover:ring-2 hover:ring-gray-300 dark:hover:ring-gray-600`
                }
              `}
              title={`${tag.tag}: ${tag.count} 次使用，最后使用于 ${formatDateTime(tag.last_used, 'MM-DD')}`}
            >
              {tag.tag}
              <span className="ml-1 text-xs opacity-60">({tag.count})</span>
            </button>
          );
        })}
      </div>

      {safeTags.length > 50 && (
        <div className="mt-4 text-center">
          <button className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300">
            显示全部 {safeTags.length} 个标签
          </button>
        </div>
      )}

      {/* 标签统计 */}
      <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600 dark:text-gray-400">最常用标签:</span>
            <div className="mt-1">
              {sortedTags.slice(0, 3).map((tag, index) => (
                <span key={tag.tag} className="inline-flex items-center">
                  {index > 0 && <span className="mx-1 text-gray-400">·</span>}
                  <span className="font-medium text-gray-900 dark:text-white">{tag.tag}</span>
                  <span className="ml-1 text-gray-500 dark:text-gray-400">({tag.count})</span>
                </span>
              ))}
            </div>
          </div>
          <div>
            <span className="text-gray-600 dark:text-gray-400">总使用次数:</span>
            <div className="mt-1 font-medium text-gray-900 dark:text-white">
              {safeTags.reduce((sum, tag) => sum + tag.count, 0)}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TagCloud;
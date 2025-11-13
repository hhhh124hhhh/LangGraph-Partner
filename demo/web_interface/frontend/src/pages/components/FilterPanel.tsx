/**
 * 过滤面板组件
 */

import React from 'react';
import Button from '@components/Button';

interface FilterPanelProps {
  selectedCategory: string;
  onCategorySelect: (category: string) => void;
  onClearFilters: () => void;
  hasActiveFilters: boolean;
  categories: string[];
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  selectedCategory,
  onCategorySelect,
  onClearFilters,
  hasActiveFilters,
  categories,
}) => {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          🔍 过滤器
        </h3>
        {hasActiveFilters && (
          <Button variant="ghost" size="sm" onClick={onClearFilters}>
            清除
          </Button>
        )}
      </div>

      {/* 分类过滤 */}
      {categories.length > 0 && (
        <div className="mb-6">
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            文档分类
          </h4>
          <div className="space-y-2">
            <label className="flex items-center cursor-pointer">
              <input
                type="radio"
                name="category"
                checked={selectedCategory === ''}
                onChange={() => onCategorySelect('')}
                className="mr-2 text-primary-600 focus:ring-primary-500"
              />
              <span className="text-sm text-gray-700 dark:text-gray-300">
                全部分类
              </span>
            </label>
            {categories.map((category) => (
              <label key={category} className="flex items-center cursor-pointer">
                <input
                  type="radio"
                  name="category"
                  checked={selectedCategory === category}
                  onChange={() => onCategorySelect(category)}
                  className="mr-2 text-primary-600 focus:ring-primary-500"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300 capitalize">
                  {category}
                </span>
              </label>
            ))}
          </div>
        </div>
      )}

      {/* 其他过滤选项（可扩展） */}
      <div className="space-y-4">
        <div>
          <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            快速过滤
          </h4>
          <div className="space-y-2">
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
              onClick={() => {
                // 这里可以添加快速过滤逻辑
              }}
            >
              📅 最近7天
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
              onClick={() => {
                // 这里可以添加快速过滤逻辑
              }}
            >
              📊 大文档 (&gt;10MB)
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="w-full justify-start"
              onClick={() => {
                // 这里可以添加快速过滤逻辑
              }}
            >
              🏷️ 无标签文档
            </Button>
          </div>
        </div>
      </div>

      {/* 过滤状态 */}
      {hasActiveFilters && (
        <div className="mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="text-sm text-gray-600 dark:text-gray-400">
            当前过滤条件:
          </div>
          <div className="mt-2 space-y-1">
            {selectedCategory && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-700 dark:text-gray-300">
                  分类: {selectedCategory}
                </span>
                <button
                  onClick={() => onCategorySelect('')}
                  className="text-red-500 hover:text-red-700"
                >
                  ✕
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterPanel;
/**
 * 搜索栏组件
 */

import React, { useState, useCallback, useRef } from 'react';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';

interface SearchBarProps {
  value: string;
  onChange: (value: string) => void;
  onSearch: (query: string) => void;
  loading?: boolean;
  placeholder?: string;
}

const SearchBar: React.FC<SearchBarProps> = ({
  value,
  onChange,
  onSearch,
  loading = false,
  placeholder = '搜索...',
}) => {
  const [focused, setFocused] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim()) {
      onSearch(value.trim());
    }
  }, [value, onSearch]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit(e as any);
    }
  }, [handleSubmit]);

  const handleClear = useCallback(() => {
    onChange('');
    inputRef.current?.focus();
  }, [onChange]);

  return (
    <div className="relative">
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          {/* 搜索图标 */}
          <div className="absolute left-3 pointer-events-none">
            {loading ? (
              <LoadingSpinner size="sm" />
            ) : (
              <svg
                className="w-5 h-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            )}
          </div>

          {/* 输入框 */}
          <input
            ref={inputRef}
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => setFocused(true)}
            onBlur={() => setFocused(false)}
            placeholder={placeholder}
            className={`
              w-full pl-10 pr-12 py-3
              bg-white dark:bg-gray-800
              border border-gray-300 dark:border-gray-600
              rounded-lg shadow-sm
              text-gray-900 dark:text-white
              placeholder-gray-500 dark:placeholder-gray-400
              focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent
              transition-all duration-200
              ${focused ? 'ring-2 ring-primary-500 border-transparent' : ''}
              ${loading ? 'cursor-wait' : ''}
            `}
            disabled={loading}
          />

          {/* 清除按钮 */}
          {value && !loading && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-12 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              title="清除搜索"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}

          {/* 搜索按钮 */}
          <Button
            type="submit"
            size="sm"
            className="absolute right-1"
            loading={loading}
            disabled={!value.trim()}
          >
            搜索
          </Button>
        </div>
      </form>

      {/* 搜索建议（可选扩展） */}
      {focused && false && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg z-10">
          {/* 搜索建议内容 */}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
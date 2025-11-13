/**
 * 文档上传模态框组件
 */

import React, { useState, useRef, useCallback } from 'react';
import { DocumentUploadRequest } from '@typesdef/index';
import Button from '@components/Button';
import LoadingSpinner from '@components/LoadingSpinner';

interface UploadModalProps {
  onClose: () => void;
  onUpload: (request: DocumentUploadRequest, onProgress?: (progress: number) => void) => Promise<void>;
  loading: boolean;
}

const UploadModal: React.FC<UploadModalProps> = ({
  onClose,
  onUpload,
  loading,
}) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  const [category, setCategory] = useState('');
  const [uploadProgress, setUploadProgress] = useState(0);
  const [dragActive, setDragActive] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const categories = [
    '技术文档',
    '项目资料',
    '学习笔记',
    '工作经验',
    '生活记录',
    '创意想法',
    '其他'
  ];

  const handleFileSelect = useCallback((file: File) => {
    // 验证文件类型
    const allowedTypes = [
      'text/plain',
      'text/markdown',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/x-markdown'
    ];

    const allowedExtensions = ['.txt', '.md', '.markdown', '.pdf', '.doc', '.docx'];
    const fileName = file.name.toLowerCase();
    const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));

    if (!hasValidExtension && !allowedTypes.includes(file.type)) {
      alert('不支持的文件类型。请上传 TXT、MD、PDF、DOC 或 DOCX 文件。');
      return;
    }

    // 验证文件大小（最大 50MB）
    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      alert('文件大小不能超过 50MB。');
      return;
    }

    setSelectedFile(file);
    // 如果没有设置标题，使用文件名作为默认标题
    if (!title) {
      const nameWithoutExt = file.name.replace(/\.[^/.]+$/, '');
      setTitle(nameWithoutExt);
    }
  }, [title]);

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  }, [handleFileSelect]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  }, [handleFileSelect]);

  const handleAddTag = useCallback(() => {
    const trimmedTag = tagInput.trim();
    if (trimmedTag && !tags.includes(trimmedTag) && tags.length < 10) {
      setTags(prev => [...prev, trimmedTag]);
      setTagInput('');
    }
  }, [tagInput, tags]);

  const handleRemoveTag = useCallback((tagToRemove: string) => {
    setTags(prev => prev.filter(tag => tag !== tagToRemove));
  }, []);

  const handleTagInputKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      handleAddTag();
    }
  }, [handleAddTag]);

  const handleUpload = useCallback(async () => {
    if (!selectedFile) {
      alert('请选择要上传的文件');
      return;
    }

    if (!title.trim()) {
      alert('请输入文档标题');
      return;
    }

    const request: DocumentUploadRequest = {
      file: selectedFile,
      title: title.trim(),
      description: description.trim() || undefined,
      tags: tags.length > 0 ? tags : undefined,
      category: category || undefined,
    };

    try {
      await onUpload(request, (progress) => {
        setUploadProgress(progress);
      });
    } catch (error) {
      console.error('上传失败:', error);
    }
  }, [selectedFile, title, description, tags, category, onUpload]);

  const handleClose = useCallback(() => {
    if (!loading) {
      onClose();
      // 重置状态
      setSelectedFile(null);
      setTitle('');
      setDescription('');
      setTags([]);
      setTagInput('');
      setCategory('');
      setUploadProgress(0);
      setDragActive(false);
    }
  }, [loading, onClose]);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            📤 上传文档
          </h2>
          <Button variant="ghost" size="sm" onClick={handleClose} disabled={loading}>
            ✕
          </Button>
        </div>

        {/* 内容 */}
        <div className="p-6">
          {/* 文件选择区域 */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              选择文件
            </label>
            <div
              className={`
                border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
                ${dragActive
                  ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                  : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                }
                ${loading ? 'pointer-events-none opacity-50' : ''}
              `}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept=".txt,.md,.markdown,.pdf,.doc,.docx"
                onChange={handleFileInputChange}
                className="hidden"
                disabled={loading}
              />

              {selectedFile ? (
                <div className="space-y-2">
                  <div className="text-4xl">📄</div>
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {selectedFile.name}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </div>
                </div>
              ) : (
                <div className="space-y-2">
                  <div className="text-4xl text-gray-400">📁</div>
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    点击选择文件或拖拽文件到此处
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-500">
                    支持 TXT、MD、PDF、DOC、DOCX 格式，最大 50MB
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* 文档信息 */}
          <div className="space-y-4">
            {/* 标题 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                标题 <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="输入文档标题"
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={loading}
              />
            </div>

            {/* 描述 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                描述
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="输入文档描述（可选）"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
                disabled={loading}
              />
            </div>

            {/* 分类 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                分类
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={loading}
              >
                <option value="">选择分类（可选）</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* 标签 */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                标签
              </label>
              <div className="flex items-center gap-2 mb-2">
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagInputKeyDown}
                  placeholder="输入标签后按回车添加"
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  disabled={loading || tags.length >= 10}
                />
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleAddTag}
                  disabled={!tagInput.trim() || tags.length >= 10}
                >
                  添加
                </Button>
              </div>
              {tags.length > 0 && (
                <div className="flex flex-wrap gap-2">
                  {tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                    >
                      {tag}
                      <button
                        type="button"
                        onClick={() => handleRemoveTag(tag)}
                        className="hover:text-blue-900 dark:hover:text-blue-100"
                        disabled={loading}
                      >
                        ✕
                      </button>
                    </span>
                  ))}
                </div>
              )}
              <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                最多添加 10 个标签
              </div>
            </div>
          </div>

          {/* 上传进度 */}
          {loading && uploadProgress > 0 && (
            <div className="mt-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">上传进度</span>
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {uploadProgress}%
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
            </div>
          )}
        </div>

        {/* 底部按钮 */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
          <Button
            variant="outline"
            onClick={handleClose}
            disabled={loading}
          >
            取消
          </Button>
          <Button
            onClick={handleUpload}
            loading={loading}
            disabled={!selectedFile || !title.trim()}
          >
            上传文档
          </Button>
        </div>
      </div>
    </div>
  );
};

export default UploadModal;
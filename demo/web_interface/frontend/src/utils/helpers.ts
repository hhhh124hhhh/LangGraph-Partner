import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { format } from 'date-fns';
import { zhCN } from 'date-fns/locale';

// 样式合并工具
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// 格式化日期时间
export function formatDateTime(date: string | Date, formatStr = 'yyyy-MM-dd HH:mm:ss'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, formatStr, { locale: zhCN });
}

// 格式化相对时间
export function formatRelativeTime(date: string | Date): string {
  const now = new Date();
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  const diffMs = now.getTime() - dateObj.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffSeconds < 60) {
    return '刚刚';
  } else if (diffMinutes < 60) {
    return `${diffMinutes}分钟前`;
  } else if (diffHours < 24) {
    return `${diffHours}小时前`;
  } else if (diffDays < 7) {
    return `${diffDays}天前`;
  } else {
    return formatDateTime(dateObj, 'yyyy-MM-dd');
  }
}

// 生成唯一ID
export function generateId(prefix = 'id'): string {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// 深度克隆对象
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as unknown as T;
  }

  if (obj instanceof Array) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }

  if (typeof obj === 'object') {
    const clonedObj = {} as T;
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }

  return obj;
}

// 防抖函数
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number,
  immediate = false
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null;

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null;
      if (!immediate) func(...args);
    };

    const callNow = immediate && !timeout;

    if (timeout) clearTimeout(timeout);
    timeout = setTimeout(later, wait);

    if (callNow) func(...args);
  };
}

// 节流函数
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;

  return function executedFunction(...args: Parameters<T>) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// 截断文本
export function truncateText(text: string, maxLength: number, suffix = '...'): string {
  if (text.length <= maxLength) return text;
  return text.substr(0, maxLength - suffix.length) + suffix;
}

// 格式化文件大小
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// 格式化数字
export function formatNumber(num: number, locale = 'zh-CN'): string {
  return new Intl.NumberFormat(locale).format(num);
}

// 格式化百分比
export function formatPercentage(value: number, decimals = 1): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

// 获取颜色值
export function getColorByValue(value: number, min = 0, max = 100): string {
  const ratio = (value - min) / (max - min);

  if (ratio < 0.33) {
    return 'text-green-600';
  } else if (ratio < 0.67) {
    return 'text-yellow-600';
  } else {
    return 'text-red-600';
  }
}

// 获取状态颜色
export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    success: 'text-green-600 bg-green-100',
    error: 'text-red-600 bg-red-100',
    warning: 'text-yellow-600 bg-yellow-100',
    info: 'text-blue-600 bg-blue-100',
    pending: 'text-gray-600 bg-gray-100',
    running: 'text-blue-600 bg-blue-100',
    completed: 'text-green-600 bg-green-100',
    failed: 'text-red-600 bg-red-100',
  };

  return statusColors[status] || 'text-gray-600 bg-gray-100';
}

// 检查是否为移动设备
export function isMobileDevice(): boolean {
  if (typeof window === 'undefined') return false;

  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
    navigator.userAgent
  );
}

// 检查是否为触摸设备
export function isTouchDevice(): boolean {
  if (typeof window === 'undefined') return false;

  return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
}

// 复制到剪贴板
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // 降级方案
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const result = document.execCommand('copy');
      textArea.remove();
      return result;
    }
  } catch (error) {
    console.error('复制失败:', error);
    return false;
  }
}

// 下载文件
export function downloadFile(data: string, filename: string, type = 'text/plain'): void {
  const blob = new Blob([data], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// 读取文件内容
export function readFileAsText(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(reader.error);
    reader.readAsText(file);
  });
}

// 验证邮箱格式
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

// 验证URL格式
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

// 生成随机颜色
export function generateRandomColor(): string {
  return `#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`;
}

// 获取对比色
export function getContrastColor(backgroundColor: string): string {
  const hex = backgroundColor.replace('#', '');
  const r = parseInt(hex.substr(0, 2), 16);
  const g = parseInt(hex.substr(2, 2), 16);
  const b = parseInt(hex.substr(4, 2), 16);
  const brightness = (r * 299 + g * 587 + b * 114) / 1000;

  return brightness > 128 ? '#000000' : '#ffffff';
}

// 本地存储工具
export const storage = {
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      if (typeof window === 'undefined') return defaultValue || null;

      const item = localStorage.getItem(key);
      if (!item) return defaultValue || null;

      return JSON.parse(item);
    } catch (error) {
      console.error('获取本地存储失败:', error);
      return defaultValue || null;
    }
  },

  set: <T>(key: string, value: T): boolean => {
    try {
      if (typeof window === 'undefined') return false;

      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('设置本地存储失败:', error);
      return false;
    }
  },

  remove: (key: string): boolean => {
    try {
      if (typeof window === 'undefined') return false;

      localStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('删除本地存储失败:', error);
      return false;
    }
  },

  clear: (): boolean => {
    try {
      if (typeof window === 'undefined') return false;

      localStorage.clear();
      return true;
    } catch (error) {
      console.error('清空本地存储失败:', error);
      return false;
    }
  },
};

// 会话存储工具
export const sessionStorage = {
  get: <T>(key: string, defaultValue?: T): T | null => {
    try {
      if (typeof window === 'undefined') return defaultValue || null;

      const item = window.sessionStorage.getItem(key);
      if (!item) return defaultValue || null;

      return JSON.parse(item);
    } catch (error) {
      console.error('获取会话存储失败:', error);
      return defaultValue || null;
    }
  },

  set: <T>(key: string, value: T): boolean => {
    try {
      if (typeof window === 'undefined') return false;

      window.sessionStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch (error) {
      console.error('设置会话存储失败:', error);
      return false;
    }
  },

  remove: (key: string): boolean => {
    try {
      if (typeof window === 'undefined') return false;

      window.sessionStorage.removeItem(key);
      return true;
    } catch (error) {
      console.error('删除会话存储失败:', error);
      return false;
    }
  },

  clear: (): boolean => {
    try {
      if (typeof window === 'undefined') return false;

      window.sessionStorage.clear();
      return true;
    } catch (error) {
      console.error('清空会话存储失败:', error);
      return false;
    }
  },
};

// 错误处理工具
export function handleError(error: unknown, context = ''): string {
  if (error instanceof Error) {
    console.error(`${context ? `[${context}] ` : ''}Error:`, error.message, error.stack);
    return error.message;
  } else if (typeof error === 'string') {
    console.error(`${context ? `[${context}] ` : ''}Error:`, error);
    return error;
  } else {
    console.error(`${context ? `[${context}] ` : ''}Unknown error:`, error);
    return '发生未知错误';
  }
}

// 重试工具
export async function retry<T>(
  fn: () => Promise<T>,
  maxAttempts = 3,
  delay = 1000
): Promise<T> {
  let lastError: Error;

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));

      if (attempt === maxAttempts) {
        throw lastError;
      }

      console.warn(`尝试 ${attempt}/${maxAttempts} 失败，${delay}ms后重试:`, lastError.message);
      await new Promise(resolve => setTimeout(resolve, delay));
      delay *= 2; // 指数退避
    }
  }

  throw lastError!;
}
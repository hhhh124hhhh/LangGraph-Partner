/**
 * 智能缓存系统
 * 提供请求缓存、去重和智能失效机制
 */

export interface CacheEntry<T = any> {
  data: T;
  timestamp: number;
  expiresAt: number;
  ttl: number;
  hits: number;
  lastAccessed: number;
  etag?: string;
}

export interface CacheOptions {
  ttl?: number; // 生存时间(毫秒)
  maxSize?: number; // 最大缓存条目数
  enableEtag?: boolean; // 启用ETag支持
  enableBackgroundRefresh?: boolean; // 启用后台刷新
  compressionEnabled?: boolean; // 启用压缩
}

export interface RequestConfig {
  url: string;
  method?: string;
  headers?: Record<string, string>;
  body?: any;
  cacheKey?: string;
  cacheOptions?: CacheOptions;
  deduplicationKey?: string;
  retryConfig?: RetryConfig;
}

export interface RetryConfig {
  maxRetries: number;
  retryDelay: number;
  retryCondition?: (error: any) => boolean;
  onRetry?: (attempt: number, error: any) => void;
}

class CacheManager {
  private cache = new Map<string, CacheEntry>();
  private pendingRequests = new Map<string, Promise<any>>();
  private defaultOptions: CacheOptions;
  private cleanupTimer?: NodeJS.Timeout;

  constructor(defaultOptions: CacheOptions = {}) {
    this.defaultOptions = {
      ttl: 5 * 60 * 1000, // 5分钟
      maxSize: 100,
      enableEtag: true,
      enableBackgroundRefresh: false,
      compressionEnabled: false,
      ...defaultOptions
    };

    // 定期清理过期缓存
    this.startCleanupTimer();
  }

  private startCleanupTimer(): void {
    this.cleanupTimer = setInterval(() => {
      this.cleanup();
    }, 60 * 1000); // 每分钟清理一次
  }

  private cleanup(): void {
    const now = Date.now();
    const entriesToDelete: string[] = [];

    // 清理过期条目
    this.cache.forEach((entry, key) => {
      if (now > entry.expiresAt) {
        entriesToDelete.push(key);
      }
    });

    // 如果缓存太大，删除最近最少使用的条目
    if (this.cache.size > this.defaultOptions.maxSize!) {
      const sortedEntries = Array.from(this.cache.entries())
        .sort((a, b) => a[1].lastAccessed - b[1].lastAccessed);

      const toDelete = sortedEntries
        .slice(0, this.cache.size - this.defaultOptions.maxSize!)
        .map(([key]) => key);

      entriesToDelete.push(...toDelete);
    }

    entriesToDelete.forEach(key => {
      this.cache.delete(key);
    });

    console.log(`[Cache] 清理完成，删除了 ${entriesToDelete.length} 个过期条目`);
  }

  private generateCacheKey(url: string, method: string = 'GET', body?: any): string {
    const keyData = {
      url,
      method: method.toUpperCase(),
      body: body ? JSON.stringify(body) : ''
    };
    return btoa(JSON.stringify(keyData)).replace(/[+/=]/g, '');
  }

  private compressData(data: any): any {
    if (!this.defaultOptions.compressionEnabled) {
      return data;
    }

    try {
      // 简单的数据压缩：移除空格和换行符
      const jsonString = JSON.stringify(data);
      return JSON.parse(jsonString.replace(/\s+/g, ' '));
    } catch (error) {
      console.warn('[Cache] 数据压缩失败:', error);
      return data;
    }
  }

  private decompressData(data: any): any {
    // 如果需要解压缩，在这里实现
    return data;
  }

  // 获取缓存
  get<T = any>(key: string): T | null {
    const entry = this.cache.get(key);

    if (!entry) {
      return null;
    }

    const now = Date.now();

    // 检查是否过期
    if (now > entry.expiresAt) {
      this.cache.delete(key);
      return null;
    }

    // 更新访问统计
    entry.hits++;
    entry.lastAccessed = now;

    console.log(`[Cache] 命中缓存: ${key} (命中率: ${entry.hits})`);
    return this.decompressData(entry.data);
  }

  // 设置缓存
  set<T = any>(key: string, data: T, options: CacheOptions = {}): void {
    const now = Date.now();
    const ttl = options.ttl || this.defaultOptions.ttl!;

    const entry: CacheEntry<T> = {
      data: this.compressData(data),
      timestamp: now,
      expiresAt: now + ttl,
      ttl,
      hits: 0,
      lastAccessed: now,
      etag: options.enableEtag ? this.generateETag(data) : undefined
    };

    this.cache.set(key, entry);
    console.log(`[Cache] 设置缓存: ${key} (TTL: ${ttl}ms)`);
  }

  // 删除缓存
  delete(key: string): boolean {
    return this.cache.delete(key);
  }

  // 清空缓存
  clear(): void {
    this.cache.clear();
    console.log('[Cache] 缓存已清空');
  }

  // 生成ETag
  private generateETag(data: any): string {
    const hash = this.simpleHash(JSON.stringify(data));
    return `"${hash}"`;
  }

  private simpleHash(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      const char = str.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // 转换为32位整数
    }
    return Math.abs(hash).toString(16);
  }

  // 检查ETag是否匹配
  checkETag(key: string, etag: string): boolean {
    const entry = this.cache.get(key);
    return entry ? entry.etag === etag : false;
  }

  // 获取缓存统计
  getStats(): {
    size: number;
    hitRate: number;
    averageHits: number;
    oldestEntry: number;
    newestEntry: number;
  } {
    if (this.cache.size === 0) {
      return {
        size: 0,
        hitRate: 0,
        averageHits: 0,
        oldestEntry: 0,
        newestEntry: 0
      };
    }

    const entries = Array.from(this.cache.values());
    const totalHits = entries.reduce((sum, entry) => sum + entry.hits, 0);
    const averageHits = totalHits / entries.length;

    const timestamps = entries.map(entry => entry.timestamp);
    const oldestEntry = Math.min(...timestamps);
    const newestEntry = Math.max(...timestamps);

    return {
      size: this.cache.size,
      hitRate: averageHits > 0 ? (averageHits / (averageHits + 1)) * 100 : 0,
      averageHits,
      oldestEntry,
      newestEntry
    };
  }

  // 预热缓存
  async warmup<T = any>(
    keys: string[],
    fetcher: (key: string) => Promise<T>,
    options: CacheOptions = {}
  ): Promise<void> {
    console.log(`[Cache] 开始预热缓存，共 ${keys.length} 个条目`);

    const promises = keys.map(async (key) => {
      try {
        const data = await fetcher(key);
        this.set(key, data, options);
      } catch (error) {
        console.warn(`[Cache] 预热失败: ${key}`, error);
      }
    });

    await Promise.all(promises);
    console.log('[Cache] 缓存预热完成');
  }

  // 后台刷新
  async backgroundRefresh<T = any>(
    key: string,
    fetcher: () => Promise<T>,
    options: CacheOptions = {}
  ): Promise<void> {
    if (!this.defaultOptions.enableBackgroundRefresh) {
      return;
    }

    const entry = this.cache.get(key);
    if (!entry) {
      return;
    }

    const now = Date.now();
    const refreshThreshold = entry.expiresAt - (entry.ttl * 0.2); // 过期前20%刷新

    if (now > refreshThreshold) {
      try {
        console.log(`[Cache] 后台刷新: ${key}`);
        const data = await fetcher();
        this.set(key, data, options);
      } catch (error) {
        console.warn(`[Cache] 后台刷新失败: ${key}`, error);
      }
    }
  }

  // 销毁缓存管理器
  destroy(): void {
    if (this.cleanupTimer) {
      clearInterval(this.cleanupTimer);
    }
    this.cache.clear();
    this.pendingRequests.clear();
  }
}

// 请求去重管理器
class RequestDeduplicator {
  private pendingRequests = new Map<string, Promise<any>>();

  private generateKey(url: string, method: string = 'GET', body?: any): string {
    return `${method}:${url}:${body ? JSON.stringify(body) : ''}`;
  }

  async deduplicate<T = any>(
    key: string,
    requestFn: () => Promise<T>
  ): Promise<T> {
    const existingRequest = this.pendingRequests.get(key);

    if (existingRequest) {
      console.log(`[Deduplicator] 请求去重: ${key}`);
      return existingRequest as Promise<T>;
    }

    const promise = requestFn().finally(() => {
      this.pendingRequests.delete(key);
    });

    this.pendingRequests.set(key, promise);
    return promise;
  }

  // 取消待处理的请求
  cancel(key: string): boolean {
    return this.pendingRequests.delete(key);
  }

  // 清空所有待处理的请求
  clear(): void {
    this.pendingRequests.clear();
  }

  // 获取待处理请求数量
  getPendingCount(): number {
    return this.pendingRequests.size;
  }
}

// 重试管理器
class RetryManager {
  async executeWithRetry<T = any>(
    requestFn: () => Promise<T>,
    config: RetryConfig
  ): Promise<T> {
    let lastError: any;

    for (let attempt = 1; attempt <= config.maxRetries; attempt++) {
      try {
        return await requestFn();
      } catch (error) {
        lastError = error;

        const shouldRetry = config.retryCondition ?
          config.retryCondition(error) :
          this.defaultRetryCondition(error);

        if (!shouldRetry || attempt === config.maxRetries) {
          break;
        }

        console.log(`[Retry] 第 ${attempt} 次重试，延迟 ${config.retryDelay}ms`);

        if (config.onRetry) {
          config.onRetry(attempt, error);
        }

        await this.delay(config.retryDelay * attempt); // 指数退避
      }
    }

    throw lastError;
  }

  private defaultRetryCondition(error: any): boolean {
    // 网络错误、5xx错误、超时等可重试
    if (!error.response) {
      return true; // 网络错误
    }

    const status = error.response.status;
    return status >= 500 || status === 408 || status === 429;
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// 创建全局实例
export const cacheManager = new CacheManager();
export const requestDeduplicator = new RequestDeduplicator();
export const retryManager = new RetryManager();

// 默认缓存选项
export const defaultCacheOptions: CacheOptions = {
  ttl: 5 * 60 * 1000, // 5分钟
  maxSize: 100,
  enableEtag: true,
  enableBackgroundRefresh: false,
  compressionEnabled: false
};

// 默认重试配置
export const defaultRetryConfig: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryCondition: undefined,
  onRetry: undefined
};

export default cacheManager;
/**
 * 增强版API服务
 * 集成缓存、去重、重试和错误处理
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError, InternalAxiosRequestConfig } from 'axios';

// 扩展Axios的InternalAxiosRequestConfig类型
declare module 'axios' {
  interface InternalAxiosRequestConfig {
    metadata?: { startTime: number };
  }
}
import { cacheManager, requestDeduplicator, retryManager, defaultCacheOptions, defaultRetryConfig } from '@utils/cache';
import { logger, apiLogger } from '@utils/logger';
import { performanceMonitor } from '@utils/performance';

export interface EnhancedRequestConfig extends AxiosRequestConfig {
  enableCache?: boolean;
  cacheOptions?: any;
  enableDeduplication?: boolean;
  deduplicationKey?: string;
  enableRetry?: boolean;
  retryConfig?: any;
  enablePerformanceLogging?: boolean;
  customErrorHandler?: (error: any) => void;
  metadata?: { startTime: number };
}

export interface ApiResponse<T = any> {
  data: T;
  status: number;
  statusText: string;
  headers: any;
  cached: boolean;
  fromCache: boolean;
  requestTime: number;
}

class EnhancedApiService {
  private axiosInstance: AxiosInstance;
  private baseURL: string;

  constructor(baseURL: string = '/api') {
    this.baseURL = baseURL;
    this.axiosInstance = this.createAxiosInstance();
  }

  private createAxiosInstance(): AxiosInstance {
    const instance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30秒超时
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    instance.interceptors.request.use(
      (config) => {
        const startTime = performance.now();
        config.metadata = { startTime };

        apiLogger.debug(`发送请求: ${config.method?.toUpperCase()} ${config.url}`, {
          headers: config.headers,
          data: config.data
        });

        return config;
      },
      (error) => {
        apiLogger.error('请求拦截器错误', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    instance.interceptors.response.use(
      (response) => {
        const endTime = performance.now();
        const duration = endTime - (response.config.metadata?.startTime || endTime);

        logger.apiRequest(
          response.config.method?.toUpperCase() || 'GET',
          response.config.url || '',
          response.status,
          duration
        );

        return response;
      },
      (error) => {
        const endTime = performance.now();
        const duration = endTime - (error.config?.metadata?.startTime || endTime);

        logger.apiRequest(
          error.config?.method?.toUpperCase() || 'GET',
          error.config?.url || '',
          error.response?.status || 0,
          duration,
          error
        );

        return Promise.reject(this.handleApiError(error));
      }
    );

    return instance;
  }

  private handleApiError(error: AxiosError): any {
    const enhancedError: any = {
      ...error,
      isApiError: true,
      timestamp: Date.now()
    };

    if (error.response) {
      // 服务器响应了错误状态码
      enhancedError.type = 'HTTP_ERROR';
      enhancedError.status = error.response.status;
      enhancedError.data = error.response.data;

      switch (error.response.status) {
        case 401:
          enhancedError.message = '认证失败，请重新登录';
          this.handleUnauthorized();
          break;
        case 403:
          enhancedError.message = '权限不足';
          break;
        case 404:
          enhancedError.message = '请求的资源不存在';
          this.handleNotFound(error.config);
          break;
        case 429:
          enhancedError.message = '请求过于频繁，请稍后再试';
          break;
        case 500:
          enhancedError.message = '服务器内部错误';
          break;
        case 502:
          enhancedError.message = '网关错误';
          break;
        case 503:
          enhancedError.message = '服务暂时不可用';
          break;
        default:
          enhancedError.message = `请求失败 (${error.response.status})`;
      }
    } else if (error.request) {
      // 请求已发出但没有收到响应
      enhancedError.type = 'NETWORK_ERROR';
      enhancedError.message = '网络连接失败，请检查网络设置';
    } else {
      // 其他错误
      enhancedError.type = 'UNKNOWN_ERROR';
      enhancedError.message = error.message || '未知错误';
    }

    return enhancedError;
  }

  private handleUnauthorized(): void {
    // 清除认证信息
    localStorage.removeItem('auth_token');

    // 可以跳转到登录页面
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
  }

  private handleNotFound(config?: AxiosRequestConfig): void {
    // 对于404错误，可以记录无效的API端点
    if (config?.url) {
      apiLogger.warn(`API端点不存在: ${config.url}`, { method: config.method });
    }
  }

  private generateCacheKey(config: EnhancedRequestConfig): string {
    const { url, method, data, params } = config;
    const keyData = {
      url: `${this.baseURL}${url}`,
      method: method?.toUpperCase() || 'GET',
      data: data || {},
      params: params || {}
    };
    return btoa(JSON.stringify(keyData)).replace(/[+/=]/g, '');
  }

  private async executeRequest<T = any>(
    config: EnhancedRequestConfig
  ): Promise<ApiResponse<T>> {
    const startTime = performance.now();
    const enableCache = config.enableCache ?? true;
    const enableDeduplication = config.enableDeduplication ?? true;
    const enableRetry = config.enableRetry ?? true;
    const enablePerformanceLogging = config.enablePerformanceLogging ?? true;

    let cacheKey: string | undefined;
    let cachedResponse: T | null = null;
    let fromCache = false;

    // 缓存检查
    if (enableCache && config.method?.toLowerCase() === 'get') {
      cacheKey = this.generateCacheKey(config);
      cachedResponse = cacheManager.get<T>(cacheKey);

      if (cachedResponse) {
        fromCache = true;
        const endTime = performance.now();
        const requestTime = endTime - startTime;

        if (enablePerformanceLogging) {
          apiLogger.performance(`Cache Hit: ${config.url}`, requestTime);
        }

        return {
          data: cachedResponse,
          status: 200,
          statusText: 'OK (from cache)',
          headers: {},
          cached: true,
          fromCache: true,
          requestTime
        };
      }
    }

    // 去重处理
    const deduplicationKey = config.deduplicationKey ||
      (enableDeduplication ? this.generateCacheKey(config) : undefined);

    const executeRequest = async (): Promise<AxiosResponse<T>> => {
      const requestConfig = { ...config };

      // 添加ETag支持
      if (enableCache && cacheKey) {
        const cachedEntry = (cacheManager as any).cache.get(cacheKey);
        if (cachedEntry?.etag) {
          requestConfig.headers = {
            ...requestConfig.headers,
            'If-None-Match': cachedEntry.etag
          };
        }
      }

      const response = await this.axiosInstance.request<T>(requestConfig);

      // 处理304 Not Modified
      if (response.status === 304 && cachedResponse) {
        return {
          ...response,
          status: 200,
          data: cachedResponse
        } as AxiosResponse<T>;
      }

      return response;
    };

    let response: AxiosResponse<T>;

    try {
      if (deduplicationKey) {
        response = await requestDeduplicator.deduplicate(deduplicationKey, executeRequest);
      } else {
        response = await executeRequest();
      }
    } catch (error) {
      // 错误处理
      if (config.customErrorHandler) {
        config.customErrorHandler(error);
      }

      // 重试逻辑
      if (enableRetry && config.method?.toLowerCase() !== 'post') {
        const retryConfig = {
          ...defaultRetryConfig,
          ...config.retryConfig
        };

        try {
          response = await retryManager.executeWithRetry(executeRequest, retryConfig);
        } catch (retryError) {
          throw retryError;
        }
      } else {
        throw error;
      }
    }

    const endTime = performance.now();
    const requestTime = endTime - startTime;

    // 缓存响应
    if (enableCache && cacheKey && response.status === 200) {
      const cacheOptions = {
        ...defaultCacheOptions,
        ...config.cacheOptions
      };

      cacheManager.set(cacheKey, response.data, cacheOptions);

      // 后台刷新
      if (cacheOptions.enableBackgroundRefresh) {
        setTimeout(() => {
          cacheManager.backgroundRefresh(cacheKey!, executeRequest, cacheOptions);
        }, cacheOptions.ttl! * 0.8);
      }
    }

    // 性能日志
    if (enablePerformanceLogging) {
      apiLogger.performance(`${config.url}`, requestTime, {
        method: config.method,
        status: response.status,
        cached: fromCache
      });
    }

    return {
      data: response.data,
      status: response.status,
      statusText: response.statusText,
      headers: response.headers,
      cached: false,
      fromCache,
      requestTime
    };
  }

  // HTTP方法封装
  async get<T = any>(url: string, config: EnhancedRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.executeRequest<T>({ ...config, method: 'GET', url });
  }

  async post<T = any>(url: string, data?: any, config: EnhancedRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.executeRequest<T>({ ...config, method: 'POST', url, data });
  }

  async put<T = any>(url: string, data?: any, config: EnhancedRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.executeRequest<T>({ ...config, method: 'PUT', url, data });
  }

  async patch<T = any>(url: string, data?: any, config: EnhancedRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.executeRequest<T>({ ...config, method: 'PATCH', url, data });
  }

  async delete<T = any>(url: string, config: EnhancedRequestConfig = {}): Promise<ApiResponse<T>> {
    return this.executeRequest<T>({ ...config, method: 'DELETE', url });
  }

  // 文件上传
  async upload<T = any>(url: string, file: File, config: EnhancedRequestConfig = {}): Promise<ApiResponse<T>> {
    const formData = new FormData();
    formData.append('file', file);

    return this.executeRequest<T>({
      ...config,
      method: 'POST',
      url,
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...config.headers
      },
      enableCache: false, // 文件上传不缓存
      enableRetry: true   // 文件上传启用重试
    });
  }

  // 批量请求
  async batch<T = any>(requests: Array<{
    method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
    url: string;
    data?: any;
    config?: EnhancedRequestConfig;
  }>): Promise<ApiResponse<T>[]> {
    const promises = requests.map(request => {
      const { method, url, data, config = {} } = request;
      return this.executeRequest<T>({ ...config, method, url, data });
    });

    return Promise.all(promises);
  }

  // 取消请求
  cancelRequest(requestId: string): boolean {
    return requestDeduplicator.cancel(requestId);
  }

  // 清空缓存
  clearCache(): void {
    cacheManager.clear();
  }

  // 预热缓存
  async warmupCache<T = any>(
    requests: Array<{ url: string; config?: EnhancedRequestConfig }>,
    fetcher: (url: string, config: EnhancedRequestConfig) => Promise<T>
  ): Promise<void> {
    const keys = requests.map(req => this.generateCacheKey({ ...req.config, method: 'GET', url: req.url }));

    await cacheManager.warmup(
      keys,
      async (key) => {
        const request = requests.find(req => this.generateCacheKey({ ...req.config, method: 'GET', url: req.url }) === key);
        if (request) {
          return await fetcher(request.url, request.config || {});
        }
        throw new Error(`Request not found for key: ${key}`);
      }
    );
  }

  // 获取API统计信息
  getStats(): {
    cache: any;
    pendingRequests: number;
  } {
    return {
      cache: cacheManager.getStats(),
      pendingRequests: requestDeduplicator.getPendingCount()
    };
  }

  // 设置认证token
  setAuthToken(token: string): void {
    this.axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }

  // 移除认证token
  removeAuthToken(): void {
    delete this.axiosInstance.defaults.headers.common['Authorization'];
  }

  // 设置基础URL
  setBaseURL(baseURL: string): void {
    this.baseURL = baseURL;
    this.axiosInstance.defaults.baseURL = baseURL;
  }
}

// 创建全局实例
export const enhancedApiService = new EnhancedApiService();

// 便捷方法
export const api = {
  get: <T = any>(url: string, config?: EnhancedRequestConfig) => enhancedApiService.get<T>(url, config),
  post: <T = any>(url: string, data?: any, config?: EnhancedRequestConfig) => enhancedApiService.post<T>(url, data, config),
  put: <T = any>(url: string, data?: any, config?: EnhancedRequestConfig) => enhancedApiService.put<T>(url, data, config),
  patch: <T = any>(url: string, data?: any, config?: EnhancedRequestConfig) => enhancedApiService.patch<T>(url, data, config),
  delete: <T = any>(url: string, config?: EnhancedRequestConfig) => enhancedApiService.delete<T>(url, config),
  upload: <T = any>(url: string, file: File, config?: EnhancedRequestConfig) => enhancedApiService.upload<T>(url, file, config)
};

export default enhancedApiService;
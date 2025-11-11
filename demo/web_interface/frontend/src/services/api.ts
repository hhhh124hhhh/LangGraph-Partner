import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  ChatRequest,
  ChatResponse,
  LangGraphState,
  PersonaUpdateRequest,
  MemoryNetwork,
  KnowledgeSearchRequest,
  KnowledgeSearchResponse,
  DemoScenario,
  ComparisonRequest,
  ComparisonResponse,
  BaseResponse
} from '@types/index';

class ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        // 可以在这里添加认证token等
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('[API] Request error:', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response: AxiosResponse) => {
        console.log(`[API] Response ${response.status}:`, response.data);
        return response;
      },
      (error: AxiosError) => {
        console.error('[API] Response error:', error.response?.data || error.message);

        // 统一错误处理
        if (error.response?.status === 401) {
          // 处理认证错误
          this.handleAuthError();
        } else if (error.response?.status >= 500) {
          // 处理服务器错误
          this.handleServerError(error);
        } else if (error.code === 'ECONNABORTED') {
          // 处理超时
          console.error('[API] Request timeout');
        }

        return Promise.reject(error);
      }
    );
  }

  private handleAuthError(): void {
    // 清除认证信息，重定向到登录页等
    console.warn('[API] Authentication required');
    // 这里可以触发全局状态更新或重定向
  }

  private handleServerError(error: AxiosError): void {
    console.error('[API] Server error:', error.response?.data);
    // 这里可以显示错误通知或发送错误报告
  }

  // 对话相关API
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<BaseResponse<ChatResponse>>('/chat/', request);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to send message');
    }
    return response.data.data;
  }

  async getChatState(sessionId: string): Promise<LangGraphState> {
    const response = await this.client.get<BaseResponse<LangGraphState>>(`/chat/state/${sessionId}`);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get chat state');
    }
    return response.data.data;
  }

  // 画像相关API
  async updatePersona(request: PersonaUpdateRequest): Promise<void> {
    const response = await this.client.post<BaseResponse>('/persona/update/', request);
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to update persona');
    }
  }

  // 记忆网络相关API
  async getMemoryNetwork(sessionId: string): Promise<MemoryNetwork> {
    const response = await this.client.get<BaseResponse<MemoryNetwork>>(`/memory/network/${sessionId}`);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get memory network');
    }
    return response.data.data;
  }

  // 知识检索相关API
  async searchKnowledge(request: KnowledgeSearchRequest): Promise<KnowledgeSearchResponse> {
    const response = await this.client.post<BaseResponse<KnowledgeSearchResponse>>('/knowledge/search/', request);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to search knowledge');
    }
    return response.data.data;
  }

  // 演示相关API
  async getDemoScenarios(): Promise<DemoScenario[]> {
    const response = await this.client.get<BaseResponse<DemoScenario[]>>('/demo/scenarios/');
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get demo scenarios');
    }
    return response.data.data;
  }

  // 对比分析相关API
  async analyzeComparison(request: ComparisonRequest): Promise<ComparisonResponse> {
    const response = await this.client.post<BaseResponse<ComparisonResponse>>('/comparison/analyze/', request);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to analyze comparison');
    }
    return response.data.data;
  }

  // 健康检查
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch (error) {
      console.error('[API] Health check failed:', error);
      return false;
    }
  }

  // 通用GET请求
  async get<T>(url: string, params?: Record<string, any>): Promise<T> {
    const response = await this.client.get<BaseResponse<T>>(url, { params });
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || `GET ${url} failed`);
    }
    return response.data.data;
  }

  // 通用POST请求
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<BaseResponse<T>>(url, data);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || `POST ${url} failed`);
    }
    return response.data.data;
  }

  // 通用PUT请求
  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.put<BaseResponse<T>>(url, data);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || `PUT ${url} failed`);
    }
    return response.data.data;
  }

  // 通用DELETE请求
  async delete<T>(url: string): Promise<T> {
    const response = await this.client.delete<BaseResponse<T>>(url);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || `DELETE ${url} failed`);
    }
    return response.data.data;
  }

  // 取消请求的token
  getCancelToken() {
    return axios.CancelToken.source();
  }

  // 检查请求是否被取消
  isCancel(error: any): boolean {
    return axios.isCancel(error);
  }
}

// 创建单例实例
export const apiService = new ApiService();
export default apiService;
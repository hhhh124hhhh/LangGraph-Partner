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
  BaseResponse,
  KnowledgeStats,
  KnowledgeDocument,
  TagStats,
  DocumentUploadRequest,
  DocumentUploadResponse,
  SimilarDocument,
  RebuildIndexResponse
} from '@typesdef/index';

class ApiService {
  private client: AxiosInstance;
  public readonly defaultModel: string;

  constructor() {
    this.client = axios.create({
      baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // 从环境变量获取默认模型
    this.defaultModel = import.meta.env.VITE_DEFAULT_MODEL || 'glm-4-flash';

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
  async sendMessage(request: ChatRequest, onChunk?: (chunk: string, metadata?: any) => void): Promise<ChatResponse> {
    const resp = await this.client.post('/chat/', request);
    const payload = resp.data as BaseResponse<any>;
    if (!payload.success || !payload.data) {
      throw new Error(payload.error || 'Failed to send message');
    }
    const data = payload.data;
    const messageText: string = data.message || data.response || data.ai_response || '';
    if (onChunk && messageText) {
      onChunk(messageText, data.metadata);
    }
    const mapped: ChatResponse = {
      message: messageText,
      session_id: data.session_id,
      persona_response: {
        applied_traits: [],
        confidence_score: 0,
        personality_markers: []
      },
      state_info: {
        current_state: 'completed',
        next_states: [],
        execution_path: []
      },
      usage: {
        tokens_used: data.metadata?.tokens_used ?? 0,
        response_time_ms: Math.round((data.processing_time ?? 0) * 1000)
      }
    };
    return mapped;
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

  async getModel(): Promise<{ model: string, env: { LLM_MODEL?: string, DEFAULT_MODEL?: string } }>{
    const response = await this.client.get<BaseResponse<{ model: string, env: { LLM_MODEL?: string, DEFAULT_MODEL?: string } }>>('/settings/model');
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get model');
    }
    return response.data.data;
  }

  async setModel(model: string): Promise<string> {
    const response = await this.client.put<BaseResponse<{ model: string }>>('/settings/model', { model });
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to set model');
    }
    return response.data.data.model;
  }

  async getSettingsConfig(): Promise<{ api_key?: string, base_url?: string, model?: string, sources?: {api_key: string, base_url: string, model: string}, has_env_config?: boolean, env_status?: string }>{
    const response = await this.client.get<BaseResponse<{ api_key?: string, base_url?: string, model?: string }>>('/settings/config');
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get settings');
    }
    return response.data.data;
  }

  async setSettingsConfig(payload: { api_key?: string, base_url?: string, model?: string }): Promise<{ api_key?: string, base_url?: string, model?: string }>{
    const response = await this.client.put<BaseResponse<{ api_key?: string, base_url?: string, model?: string }>>('/settings/config', payload);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to update settings');
    }
    return response.data.data;
  }

  async validateSettings(payload?: { api_key?: string, base_url?: string }): Promise<{ valid: boolean, models: string[] }>{
    const response = await this.client.post<BaseResponse<{ valid: boolean, models: string[] }>>('/settings/validate', payload || {});
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to validate settings');
    }
    return response.data.data;
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

  // ============ 知识库管理API ============

  // 获取知识库统计信息
  async getKnowledgeStats(): Promise<KnowledgeStats> {
    const response = await this.client.get<BaseResponse<KnowledgeStats>>('/knowledge/stats');
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get knowledge stats');
    }
    return response.data.data;
  }

  // 语义搜索
  async searchKnowledgeDocuments(request: KnowledgeSearchRequest): Promise<KnowledgeSearchResponse> {
    const response = await this.client.post<BaseResponse<KnowledgeSearchResponse>>('/knowledge/search', request);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to search documents');
    }
    return response.data.data;
  }

  // 获取文档列表
  async getKnowledgeDocuments(params?: {
    page?: number;
    page_size?: number;
    tags?: string[];
    category?: string;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
  }): Promise<{
    documents: KnowledgeDocument[];
    total: number;
    page: number;
    page_size: number;
    total_pages: number;
  }> {
    const response = await this.client.get<BaseResponse<{
      documents: KnowledgeDocument[];
      total: number;
      page: number;
      page_size: number;
      total_pages: number;
    }>>('/knowledge/documents', { params });
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get documents');
    }
    return response.data.data;
  }

  // 获取文档详情
  async getKnowledgeDocument(docId: string): Promise<KnowledgeDocument> {
    const response = await this.client.get<BaseResponse<KnowledgeDocument>>(`/knowledge/documents/${docId}`);
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get document details');
    }
    return response.data.data;
  }

  // 上传文档
  async uploadDocument(request: DocumentUploadRequest, onProgress?: (progress: number) => void): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', request.file);

    if (request.title) {
      formData.append('title', request.title);
    }
    if (request.description) {
      formData.append('description', request.description);
    }
    if (request.category) {
      formData.append('category', request.category);
    }
    if (request.tags && request.tags.length > 0) {
      formData.append('tags', JSON.stringify(request.tags));
    }

    const response = await this.client.post<BaseResponse<DocumentUploadResponse>>('/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });

    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to upload document');
    }
    return response.data.data;
  }

  // 删除文档
  async deleteKnowledgeDocument(docId: string): Promise<void> {
    const response = await this.client.delete<BaseResponse>(`/knowledge/documents/${docId}`);
    if (!response.data.success) {
      throw new Error(response.data.error || 'Failed to delete document');
    }
  }

  // 获取标签统计
  async getKnowledgeTags(): Promise<TagStats[]> {
    const response = await this.client.get<BaseResponse<TagStats[]>>('/knowledge/tags');
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get tags');
    }
    return response.data.data;
  }

  // 重建索引
  async rebuildKnowledgeIndex(): Promise<RebuildIndexResponse> {
    const response = await this.client.post<BaseResponse<RebuildIndexResponse>>('/knowledge/rebuild');
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to rebuild index');
    }
    return response.data.data;
  }

  // 获取相似文档
  async getSimilarDocuments(docId: string, limit?: number): Promise<SimilarDocument[]> {
    const response = await this.client.get<BaseResponse<SimilarDocument[]>>(`/knowledge/similar/${docId}`, {
      params: { limit }
    });
    if (!response.data.success || !response.data.data) {
      throw new Error(response.data.error || 'Failed to get similar documents');
    }
    return response.data.data;
  }
}

// 创建单例实例
export const apiService = new ApiService();
export default apiService;

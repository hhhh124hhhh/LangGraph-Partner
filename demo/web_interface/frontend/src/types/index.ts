// 基础类型定义
export interface BaseResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

// 用户画像相关
export interface Persona {
  id: string;
  name: string;
  description: string;
  personality_traits: string[];
  interests: string[];
  communication_style: string;
  expertise_areas: string[];
  created_at: string;
  updated_at: string;
}

export interface PersonaUpdateRequest {
  session_id: string;
  traits: Record<string, any>;
  preferences: Record<string, any>;
  context: string;
}

// 对话相关
export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  session_id: string;
  metadata?: {
    persona_influence?: string;
    confidence?: number;
    related_memories?: string[];
    knowledge_sources?: string[];
  };
}

export interface ChatRequest {
  message: string;
  session_id: string;
  persona_id?: string;
  context?: Record<string, any>;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  persona_response: {
    applied_traits: string[];
    confidence_score: number;
    personality_markers: string[];
  };
  state_info: {
    current_state: string;
    next_states: string[];
    execution_path: string[];
  };
  usage: {
    tokens_used: number;
    response_time_ms: number;
  };
}

// LangGraph状态相关
export interface LangGraphState {
  session_id: string;
  current_node: string;
  status: 'running' | 'completed' | 'error' | 'waiting';
  progress: number;
  nodes: GraphNode[];
  edges: GraphEdge[];
  metadata: {
    execution_time: number;
    tokens_processed: number;
    error_count: number;
  };
}

export interface GraphNode {
  id: string;
  type: 'start' | 'process' | 'decision' | 'end' | 'tool';
  label: string;
  status: 'pending' | 'running' | 'completed' | 'error';
  position: { x: number; y: number };
  metadata: {
    execution_time?: number;
    input?: any;
    output?: any;
    error?: string;
  };
}

export interface GraphEdge {
  id: string;
  source: string;
  target: string;
  label?: string;
  condition?: string;
  status: 'pending' | 'active' | 'completed';
}

// 记忆网络相关
export interface MemoryNetwork {
  session_id: string;
  nodes: MemoryNode[];
  edges: MemoryEdge[];
  clusters: MemoryCluster[];
  metrics: {
    total_memories: number;
    connection_strength: number;
    topic_diversity: number;
    temporal_span_days: number;
  };
}

export interface MemoryNode {
  id: string;
  type: 'conversation' | 'fact' | 'preference' | 'emotion' | 'knowledge';
  content: string;
  importance: number;
  timestamp: string;
  keywords: string[];
  embedding?: number[];
  metadata: {
    source?: string;
    confidence?: number;
    verification_status?: 'verified' | 'unverified' | 'disputed';
  };
}

export interface MemoryEdge {
  id: string;
  source: string;
  target: string;
  weight: number;
  type: 'semantic' | 'temporal' | 'causal' | 'emotional';
  strength: number;
}

export interface MemoryCluster {
  id: string;
  label: string;
  nodes: string[];
  coherence_score: number;
  main_topics: string[];
}

// 知识检索相关
export interface KnowledgeSearchRequest {
  query: string;
  session_id?: string;
  filters?: {
    domain?: string;
    confidence_min?: number;
    recency_days?: number;
  };
  limit?: number;
}

export interface KnowledgeSearchResponse {
  results: KnowledgeItem[];
  total_count: number;
  search_time_ms: number;
  query_analysis: {
    intent: string;
    entities: string[];
    topics: string[];
  };
}

export interface KnowledgeItem {
  id: string;
  content: string;
  source: string;
  confidence: number;
  relevance_score: number;
  metadata: {
    created_at: string;
    updated_at: string;
    author?: string;
    verification_status?: string;
    tags: string[];
  };
  highlights?: string[];
}

// 演示场景相关
export interface DemoScenario {
  id: string;
  name: string;
  description: string;
  category: 'conversation' | 'visualization' | 'comparison' | 'integration';
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  steps: DemoStep[];
  expected_outcomes: string[];
  prerequisites: string[];
}

export interface DemoStep {
  id: string;
  title: string;
  description: string;
  action_type: 'chat' | 'navigate' | 'observe' | 'interact';
  parameters: Record<string, any>;
  validation: {
    type: string;
    expected_value?: any;
    condition?: string;
  };
}

// 对比分析相关
export interface ComparisonRequest {
  session_id: string;
  metrics: string[];
  time_range?: {
    start: string;
    end: string;
  };
  baseline?: {
    platform: 'coze' | 'other';
    config: Record<string, any>;
  };
}

export interface ComparisonResponse {
  langgraph_metrics: MetricData[];
  baseline_metrics?: MetricData[];
  comparison_summary: {
    overall_winner: string;
    improvement_percentage: Record<string, number>;
    key_insights: string[];
  };
  detailed_analysis: {
    response_quality: QualityAnalysis;
    efficiency_metrics: EfficiencyAnalysis;
    user_satisfaction: SatisfactionAnalysis;
  };
}

export interface MetricData {
  name: string;
  value: number;
  unit: string;
  trend: 'up' | 'down' | 'stable';
  confidence: number;
  breakdown?: Record<string, number>;
}

export interface QualityAnalysis {
  relevance_score: number;
  coherence_score: number;
  personalization_score: number;
  accuracy_score: number;
  creativity_score: number;
}

export interface EfficiencyAnalysis {
  response_time_ms: number;
  token_efficiency: number;
  resource_utilization: number;
  success_rate: number;
  error_rate: number;
}

export interface SatisfactionAnalysis {
  user_rating: number;
  engagement_level: number;
  task_completion_rate: number;
  retention_rate: number;
}

// UI状态相关
export interface UIState {
  theme: 'light' | 'dark' | 'system';
  sidebar_open: boolean;
  active_panel: string;
  notifications: Notification[];
  loading: {
    global: boolean;
    components: Record<string, boolean>;
  };
}

export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  duration?: number;
  actions?: NotificationAction[];
}

export interface NotificationAction {
  label: string;
  action: string;
  primary?: boolean;
}

// 实时更新相关
export interface WebSocketMessage {
  type: 'state_update' | 'message_update' | 'memory_update' | 'error' | 'ping' | 'connection_error' | 'connection_opened' | 'connection_closed' | 'connection_quality_update';
  payload: any;
  timestamp: string;
  session_id?: string;
}

// 组件Props类型
export interface ComponentProps {
  className?: string;
  children?: React.ReactNode;
}

// 图表数据类型
export interface ChartData {
  name: string;
  value: number;
  color?: string;
  metadata?: Record<string, any>;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  category?: string;
}

// 表单数据类型
export interface FormField {
  name: string;
  type: 'text' | 'textarea' | 'select' | 'checkbox' | 'radio' | 'number';
  label: string;
  placeholder?: string;
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
  validation?: {
    min?: number;
    max?: number;
    pattern?: string;
    message?: string;
  };
}
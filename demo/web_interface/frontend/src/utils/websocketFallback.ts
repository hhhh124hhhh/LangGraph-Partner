/**
 * WebSocket 降级方案
 * 当WebSocket连接失败时提供模拟数据和功能
 */

export interface FallbackMessage {
  type: string;
  payload: any;
  timestamp: string;
}

export interface MockData {
  // 模拟对话数据
  chatMessages: Array<{
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }>;

  // 模拟状态数据
  langGraphState: {
    status: 'idle' | 'running' | 'completed' | 'error';
    current_node?: string;
    execution_time?: number;
  };

  // 模拟记忆网络数据
  memoryNetwork: {
    nodes: Array<{
      id: string;
      label: string;
      type: 'user' | 'assistant' | 'context';
    }>;
    edges: Array<{
      source: string;
      target: string;
      type: 'response' | 'context' | 'memory';
    }>;
  };
}

class WebSocketFallback {
  private eventHandlers: Map<string, Set<Function>> = new Map();
  private isConnected = false;
  private mockData: MockData;
  private intervalId?: NodeJS.Timeout;

  constructor() {
    this.initializeMockData();
    this.setupEventHandlers();
  }

  private initializeMockData(): void {
    this.mockData = {
      chatMessages: [
        {
          id: '1',
          role: 'user',
          content: '你好，AI Partner！',
          timestamp: new Date().toISOString()
        },
        {
          id: '2',
          role: 'assistant',
          content: '您好！我是AI Partner智能体，很高兴为您服务。我可以帮助您进行对话分析、记忆管理和数据可视化。',
          timestamp: new Date().toISOString()
        }
      ],
      langGraphState: {
        status: 'idle',
        current_node: 'start',
        execution_time: 0
      },
      memoryNetwork: {
        nodes: [
          { id: '1', label: '用户', type: 'user' },
          { id: '2', label: 'AI Partner', type: 'assistant' },
          { id: '3', label: '当前对话', type: 'context' }
        ],
        edges: [
          { source: '1', target: '2', type: 'response' },
          { source: '2', target: '3', type: 'context' }
        ]
      }
    };
  }

  private setupEventHandlers(): void {
    const eventTypes = [
      'state_update',
      'message_update',
      'memory_update',
      'error',
      'ping',
      'connection_opened',
      'connection_closed',
      'connection_error'
    ];

    eventTypes.forEach(type => {
      this.eventHandlers.set(type, new Set());
    });
  }

  // 模拟连接
  async connect(): Promise<void> {
    return new Promise((resolve) => {
      setTimeout(() => {
        this.isConnected = true;
        this.emit({
          type: 'connection_opened',
          payload: { connected: true, fallback: true },
          timestamp: new Date().toISOString()
        });
        resolve();
      }, 1000);
    });
  }

  // 模拟断开连接
  disconnect(): void {
    this.isConnected = false;
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    this.emit({
      type: 'connection_closed',
      payload: { code: 1000, reason: 'Fallback disconnect' },
      timestamp: new Date().toISOString()
    });
  }

  // 模拟发送消息
  send(message: any): void {
    if (!this.isConnected) return;

    const { type, payload } = message;

    switch (type) {
      case 'ping':
        setTimeout(() => {
          this.emit({
            type: 'ping',
            payload: {},
            timestamp: new Date().toISOString()
          });
        }, 100);
        break;

      case 'subscribe':
        this.startMockUpdates();
        break;

      case 'unsubscribe':
        this.stopMockUpdates();
        break;

      case 'chat_message':
        this.simulateChatResponse(payload);
        break;

      default:
        console.log('[WebSocket Fallback] 模拟发送消息:', type, payload);
    }
  }

  // 开始模拟数据更新
  private startMockUpdates(): void {
    if (this.intervalId) return;

    this.intervalId = setInterval(() => {
      this.simulateStateUpdate();
    }, 3000);
  }

  // 停止模拟数据更新
  private stopMockUpdates(): void {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = undefined;
    }
  }

  // 模拟状态更新
  private simulateStateUpdate(): void {
    const statuses = ['idle', 'running', 'completed'];
    const randomStatus = statuses[Math.floor(Math.random() * statuses.length)];

    this.mockData.langGraphState = {
      ...this.mockData.langGraphState,
      status: randomStatus as any,
      execution_time: Math.floor(Math.random() * 5000)
    };

    this.emit({
      type: 'state_update',
      payload: {
        langGraphState: this.mockData.langGraphState
      },
      timestamp: new Date().toISOString()
    });
  }

  // 模拟对话响应
  private simulateChatResponse(userMessage: any): void {
    setTimeout(() => {
      const assistantMessage = {
        id: String(Date.now()),
        role: 'assistant' as const,
        content: this.generateMockResponse(userMessage.content),
        timestamp: new Date().toISOString()
      };

      this.mockData.chatMessages.push(assistantMessage);

      this.emit({
        type: 'message_update',
        payload: {
          message: assistantMessage,
          messages: this.mockData.chatMessages
        },
        timestamp: new Date().toISOString()
      });
    }, 1500);
  }

  // 生成模拟回复
  private generateMockResponse(userContent: string): string {
    const responses = [
      '这是一个很有趣的问题！让我为您分析一下...',
      '基于您的需求，我建议我们采用以下方案...',
      '我理解您的意思，让我为您提供更详细的解答...',
      '这是一个很好的观察！我们可以从多个角度来分析这个问题...',
      '感谢您的反馈！我会根据您的建议进行调整...'
    ];

    return responses[Math.floor(Math.random() * responses.length)];
  }

  // 事件监听器管理
  on(eventType: string, handler: Function): () => void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.add(handler);
    }

    return () => {
      const handlers = this.eventHandlers.get(eventType);
      if (handlers) {
        handlers.delete(handler);
      }
    };
  }

  once(eventType: string, handler: Function): void {
    const onceHandler = (message: any) => {
      handler(message);
      const handlers = this.eventHandlers.get(eventType);
      if (handlers) {
        handlers.delete(onceHandler);
      }
    };

    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.add(onceHandler);
    }
  }

  off(eventType: string, handler: Function): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  private emit(message: FallbackMessage): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('[WebSocket Fallback] Handler error:', error);
        }
      });
    }
  }

  // 获取模拟数据
  getMockData(): MockData {
    return { ...this.mockData };
  }

  // 更新模拟数据
  updateMockData(newData: Partial<MockData>): void {
    this.mockData = { ...this.mockData, ...newData };
  }

  // 连接状态
  get connected(): boolean {
    return this.isConnected;
  }

  get readyState(): number {
    return this.isConnected ? 1 : 3; // WebSocket.OPEN = 1, WebSocket.CLOSED = 3
  }

  // 清理资源
  destroy(): void {
    this.disconnect();
    this.eventHandlers.clear();
  }
}

// 创建降级方案实例
export const webSocketFallback = new WebSocketFallback();
export default webSocketFallback;
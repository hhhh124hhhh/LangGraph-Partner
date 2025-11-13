import { WebSocketMessage, UIState, Notification } from '@typesdef/index';

export type WebSocketEventHandler = (message: WebSocketMessage) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map();
  private pingInterval: NodeJS.Timeout | null = null;
  private _isConnecting = false;

  constructor() {
    this.setupEventHandlers();
  }

  private setupEventHandlers(): void {
    // 初始化事件处理器集合
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

  connect(url?: string): Promise<void> {
    if (this._isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve();
    }

    this._isConnecting = true;

    const wsUrl = url || this.getWebSocketUrl();
    console.log('[WebSocket] Connecting to:', wsUrl);

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this._isConnecting = false;
          this.reconnectAttempts = 0;
          this.startPingInterval();
          this.emit({ type: 'connection_opened', payload: { connected: true }, timestamp: new Date().toISOString() });
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('[WebSocket] Disconnected:', event.code, event.reason);
          this._isConnecting = false;
          this.stopPingInterval();
          this.emit({ type: 'connection_closed', payload: { code: event.code, reason: event.reason }, timestamp: new Date().toISOString() });
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          this._isConnecting = false;
          this.emit({ type: 'connection_error', payload: { error }, timestamp: new Date().toISOString() });
          reject(error);
        };
      } catch (error) {
        this._isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  send(message: Omit<WebSocketMessage, 'timestamp'>): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const fullMessage: WebSocketMessage = {
        ...message,
        timestamp: new Date().toISOString()
      };
      this.ws.send(JSON.stringify(fullMessage));
    } else {
      console.warn('[WebSocket] Cannot send message, not connected');
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    console.log('[WebSocket] Received:', message);

    switch (message.type) {
      case 'ping':
        this.handlePing();
        break;
      case 'state_update':
      case 'message_update':
      case 'memory_update':
      case 'error':
        this.emit(message);
        break;
      default:
        console.warn('[WebSocket] Unknown message type:', message.type);
    }
  }

  private handlePing(): void {
    this.send({ type: 'ping', payload: {} });
  }

  private emit(message: WebSocketMessage): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          console.error('[WebSocket] Handler error:', error);
        }
      });
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);

      console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

      setTimeout(() => {
        this.connect().catch(error => {
          console.error('[WebSocket] Reconnection failed:', error);
        });
      }, delay);
    } else {
      console.error('[WebSocket] Max reconnection attempts reached');
    }
  }

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping', payload: {} });
    }, 30000); // 每30秒发送一次ping
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = import.meta.env.VITE_WS_URL || `${protocol}//${host}/ws`;
    return wsUrl;
  }

  // 事件监听器管理
  on(eventType: string, handler: WebSocketEventHandler): () => void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.add(handler);
    }

    // 返回取消监听的函数
    return () => {
      const handlers = this.eventHandlers.get(eventType);
      if (handlers) {
        handlers.delete(handler);
      }
    };
  }

  once(eventType: string, handler: WebSocketEventHandler): void {
    const onceHandler = (message: WebSocketMessage) => {
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

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  // 获取连接状态
  get readyState(): number {
    return this.ws?.readyState ?? WebSocket.CLOSED;
  }

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  get isConnecting(): boolean {
    return this._isConnecting;
  }
}

// 创建单例实例
export const webSocketService = new WebSocketService();
export default webSocketService;
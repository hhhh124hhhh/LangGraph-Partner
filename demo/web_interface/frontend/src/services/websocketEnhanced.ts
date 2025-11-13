/**
 * 增强版 WebSocket 服务
 * 集成连接状态管理器和健壮的错误处理
 */

import { WebSocketMessage } from '@typesdef/index';
import { connectionManager, ConnectionState } from '@utils/connectionManager';

export type WebSocketEventHandler = (message: WebSocketMessage) => void;

interface WebSocketConfig {
  maxReconnectAttempts?: number;
  baseReconnectDelay?: number;
  maxReconnectDelay?: number;
  connectionTimeout?: number;
  heartbeatInterval?: number;
}

class EnhancedWebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map();
  private pingInterval: NodeJS.Timeout | null = null;
  private _isConnecting = false;
  private manualDisconnect = false;
  private config: WebSocketConfig;

  constructor(config: WebSocketConfig = {}) {
    this.config = {
      maxReconnectAttempts: 10,
      baseReconnectDelay: 1000,
      maxReconnectDelay: 30000,
      connectionTimeout: 10000,
      heartbeatInterval: 30000,
      ...config
    };

    this.setupEventHandlers();
    this.setupConnectionManager();
  }

  private setupEventHandlers(): void {
    const eventTypes = [
      'state_update',
      'message_update',
      'memory_update',
      'error',
      'ping',
      'message',
      'message_response',
      'connection_opened',
      'connection_closed',
      'connection_error',
      'connection_quality_update'
    ];

    eventTypes.forEach(type => {
      this.eventHandlers.set(type, new Set());
    });
  }

  private setupConnectionManager(): void {
    // 监听连接状态变化
    connectionManager.onStateChange((state) => {
      console.log(`[WebSocket] Connection state: ${state}`);

      // 发送连接状态更新事件
      this.emit({
        type: 'connection_quality_update',
        payload: {
          state,
          metrics: connectionManager.getMetrics(),
          quality: connectionManager.getConnectionQuality()
        },
        timestamp: new Date().toISOString()
      });
    });
  }

  async connect(url?: string): Promise<void> {
    if (this._isConnecting || (this.ws && this.ws.readyState === WebSocket.OPEN)) {
      return Promise.resolve();
    }

    this._isConnecting = true;
    this.manualDisconnect = false;

    const isReconnect = this.reconnectAttempts > 0;
    const currentState = isReconnect ? ConnectionState.RECONNECTING : ConnectionState.CONNECTING;

    connectionManager.setState(currentState);
    connectionManager.startConnectionTimer();

    const wsUrl = url || this.getWebSocketUrl();
    console.log(`[WebSocket] ${isReconnect ? 'Reconnecting' : 'Connecting'} to:`, wsUrl);

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(wsUrl);

        const connectionTimer = setTimeout(() => {
          if (this._isConnecting) {
            connectionManager.onConnectionFailure();
            this.cleanup();
            reject(new Error('Connection timeout'));
          }
        }, this.config.connectionTimeout);

        this.ws.onopen = () => {
          clearTimeout(connectionTimer);
          console.log('[WebSocket] Connected');
          this._isConnecting = false;
          this.reconnectAttempts = 0;
          this.startPingInterval();
          connectionManager.onConnectionSuccess();

          this.emit({
            type: 'connection_opened',
            payload: {
              connected: true,
              attempt: this.reconnectAttempts,
              quality: connectionManager.getConnectionQuality()
            },
            timestamp: new Date().toISOString()
          });

          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
            // 发送解析错误通知
            this.emit({
              type: 'error',
              payload: {
                error: 'Message parse error',
                originalData: event.data
              },
              timestamp: new Date().toISOString()
            });
          }
        };

        this.ws.onclose = (event) => {
          clearTimeout(connectionTimer);
          console.log('[WebSocket] Disconnected:', event.code, event.reason);
          this._isConnecting = false;
          this.stopPingInterval();
          connectionManager.onDisconnection();

          this.emit({
            type: 'connection_closed',
            payload: {
              code: event.code,
              reason: event.reason,
              wasClean: event.wasClean
            },
            timestamp: new Date().toISOString()
          });

          // 只有在非手动断开时才尝试重连
          if (!this.manualDisconnect) {
            this.handleReconnect();
          }
        };

        this.ws.onerror = (error) => {
          clearTimeout(connectionTimer);
          console.error('[WebSocket] Error:', error);
          this._isConnecting = false;
          connectionManager.onConnectionFailure();

          this.emit({
            type: 'connection_error',
            payload: {
              error: error,
              attempt: this.reconnectAttempts
            },
            timestamp: new Date().toISOString()
          });

          reject(error);
        };
      } catch (error) {
        connectionManager.onConnectionFailure();
        this._isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.manualDisconnect = true;

    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }

    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }

    connectionManager.onDisconnection();
    console.log('[WebSocket] Manually disconnected');
  }

  send(message: Omit<WebSocketMessage, 'timestamp'>): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        const fullMessage: WebSocketMessage = {
          ...message,
          timestamp: new Date().toISOString()
        };
        this.ws.send(JSON.stringify(fullMessage));
        return true;
      } catch (error) {
        console.error('[WebSocket] Send error:', error);
        return false;
      }
    } else {
      console.warn('[WebSocket] Cannot send message, not connected');
      return false;
    }
  }

  private handleMessage(message: WebSocketMessage): void {
    // 减少日志输出，只对重要消息记录
    if (message.type !== 'ping') {
      console.log('[WebSocket] Received:', message.type);
    }

    switch (message.type) {
      case 'ping':
        this.handlePing();
        break;
      case 'message':
      case 'message_response':
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
    this.send({ type: 'pong', payload: {} });
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
    const config = connectionManager.getConfig();

    if (this.reconnectAttempts < config.maxReconnectAttempts) {
      this.reconnectAttempts++;
      connectionManager.onReconnectStart();

      const delay = connectionManager.calculateReconnectDelay(this.reconnectAttempts);
      const metrics = connectionManager.getMetrics();
      const quality = connectionManager.getConnectionQuality();

      console.log(
        `[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${config.maxReconnectAttempts}) - Quality: ${quality}%`
      );

      setTimeout(async () => {
        try {
          await this.connect();
        } catch (error) {
          console.error('[WebSocket] Reconnection failed:', error);

          // 如果重连失败，发送错误通知
          this.emit({
            type: 'error',
            payload: {
              error: 'Reconnection failed',
              attempt: this.reconnectAttempts,
              nextRetryIn: connectionManager.calculateReconnectDelay(this.reconnectAttempts + 1),
              quality
            },
            timestamp: new Date().toISOString()
          });
        }
      }, delay);
    } else {
      console.error('[WebSocket] Max reconnection attempts reached');
      connectionManager.setState(ConnectionState.ERROR);

      // 发送最终错误通知
      this.emit({
        type: 'error',
        payload: {
          error: 'Max reconnection attempts reached',
          totalAttempts: this.reconnectAttempts,
          metrics: connectionManager.getMetrics()
        },
        timestamp: new Date().toISOString()
      });
    }
  }

  private startPingInterval(): void {
    this.stopPingInterval();
    this.pingInterval = setInterval(() => {
      this.send({ type: 'ping', payload: {} });
    }, this.config.heartbeatInterval);
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private getWebSocketUrl(): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // 修复：明确使用后端服务器地址，而不是当前页面地址
    const host = import.meta.env.VITE_WS_URL ?
      new URL(import.meta.env.VITE_WS_URL).host :
      'localhost:8000';
    const wsUrl = `${protocol}//${host}/ws`;
    console.log('[WebSocket] Connecting to:', wsUrl);
    return wsUrl;
  }

  private cleanup(): void {
    this._isConnecting = false;
    if (this.ws) {
      this.ws = null;
    }
    this.stopPingInterval();
  }

  // 事件监听器管理
  on(eventType: string, handler: WebSocketEventHandler): () => void {
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

  get connectionState(): ConnectionState {
    return connectionManager.getState();
  }

  get connectionMetrics() {
    return connectionManager.getMetrics();
  }

  get connectionQuality(): number {
    return connectionManager.getConnectionQuality();
  }

  // 获取完整的连接状态信息
  get connectionStatus(): any {
    return {
      state: this.connectionState,
      quality: this.connectionQuality,
      metrics: this.connectionMetrics
    };
  }

  // 获取重连统计
  get reconnectStats() {
    return {
      attempts: this.reconnectAttempts,
      maxAttempts: connectionManager.getConfig().maxReconnectAttempts,
      nextRetryDelay: this.reconnectAttempts > 0 ?
        connectionManager.calculateReconnectDelay(this.reconnectAttempts + 1) : 0
    };
  }

  // 销毁服务实例
  destroy(): void {
    this.disconnect();
    this.eventHandlers.clear();
    this.cleanup();
  }
}

// 创建增强版实例
export const enhancedWebSocketService = new EnhancedWebSocketService();
export default enhancedWebSocketService;

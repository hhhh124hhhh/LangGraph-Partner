/**
 * WebSocket 管理器
 * 集成WebSocket和降级方案的统一接口
 */

import { enhancedWebSocketService } from './websocketEnhanced';
import { webSocketFallback } from '@utils/websocketFallback';
import { logger } from '@utils/logger';

export type WebSocketEventHandler = (message: any) => void;

export enum ConnectionMode {
  WEBSOCKET = 'websocket',
  FALLBACK = 'fallback',
  OFFLINE = 'offline'
}

class WebSocketManager {
  private currentMode: ConnectionMode = ConnectionMode.OFFLINE;
  private eventHandlers: Map<string, Set<WebSocketEventHandler>> = new Map();
  private _isConnecting = false;
  private maxRetries = 3;
  private retryCount = 0;

  constructor() {
    this.setupEventHandlers();
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
      'connection_error',
      'connection_quality_update'
    ];

    eventTypes.forEach(type => {
      this.eventHandlers.set(type, new Set());
    });
  }

  // 尝试连接WebSocket
  async connect(url?: string): Promise<void> {
    if (this._isConnecting) return;

    this._isConnecting = true;

    try {
      logger.info('[WebSocket Manager] 尝试WebSocket连接', 'WebSocket');

      // 首先尝试WebSocket连接
      await enhancedWebSocketService.connect(url);

      // WebSocket连接成功
      this.currentMode = ConnectionMode.WEBSOCKET;
      this.retryCount = 0;
      this._isConnecting = false;

      // 绑定WebSocket事件
      this.bindWebSocketEvents();

      logger.info('[WebSocket Manager] WebSocket连接成功', 'WebSocket');

      this.emit({
        type: 'connection_opened',
        payload: {
          connected: true,
          mode: 'websocket',
          quality: enhancedWebSocketService.connectionQuality
        },
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      logger.warn('[WebSocket Manager] WebSocket连接失败，尝试降级方案', 'WebSocket', error);

      // WebSocket连接失败，使用降级方案
      await this.connectFallback();
    }
  }

  // 使用降级方案连接
  private async connectFallback(): Promise<void> {
    try {
      await webSocketFallback.connect();
      this.currentMode = ConnectionMode.FALLBACK;
      this._isConnecting = false;

      // 绑定降级方案事件
      this.bindFallbackEvents();

      logger.info('[WebSocket Manager] 降级方案连接成功', 'WebSocket');

      this.emit({
        type: 'connection_opened',
        payload: {
          connected: true,
          mode: 'fallback',
          quality: 60 // 降级方案给予60%的质量分数
        },
        timestamp: new Date().toISOString()
      });

    } catch (error) {
      logger.error('[WebSocket Manager] 所有连接方案都失败', 'WebSocket', error);
      this.currentMode = ConnectionMode.OFFLINE;
      this._isConnecting = false;

      this.emit({
        type: 'connection_error',
        payload: {
          error: '所有连接方案都失败',
          mode: 'offline'
        },
        timestamp: new Date().toISOString()
      });
    }
  }

  // 绑定WebSocket事件
  private bindWebSocketEvents(): void {
    // 清理之前的绑定
    this.unbindAllEvents();

    // 绑定新事件
    enhancedWebSocketService.on('connection_opened', (message) => {
      this.emit({
        ...message,
        payload: { ...message.payload, mode: 'websocket' }
      });
    });

    enhancedWebSocketService.on('connection_closed', (message) => {
      this.emit({
        ...message,
        payload: { ...message.payload, mode: 'websocket' }
      });

      // WebSocket断开，尝试降级方案
      if (this.currentMode === ConnectionMode.WEBSOCKET) {
        this.handleWebSocketDisconnect();
      }
    });

    enhancedWebSocketService.on('connection_error', (message) => {
      this.emit({
        ...message,
        payload: { ...message.payload, mode: 'websocket' }
      });
    });

    enhancedWebSocketService.on('connection_quality_update', (message) => {
      this.emit(message);
    });

    // 转发其他事件
    ['state_update', 'message_update', 'memory_update', 'error', 'ping', 'message', 'message_response'].forEach(eventType => {
      enhancedWebSocketService.on(eventType, (message) => {
        this.emit(message);
      });
    });
  }

  // 绑定降级方案事件
  private bindFallbackEvents(): void {
    // 清理之前的绑定
    this.unbindAllEvents();

    // 绑定新事件
    webSocketFallback.on('connection_opened', (message) => {
      this.emit({
        ...message,
        payload: { ...message.payload, mode: 'fallback' }
      });
    });

    webSocketFallback.on('connection_closed', (message) => {
      this.emit({
        ...message,
        payload: { ...message.payload, mode: 'fallback' }
      });
    });

    // 转发其他事件
    ['state_update', 'message_update', 'memory_update', 'error', 'ping', 'message', 'message_response'].forEach(eventType => {
      webSocketFallback.on(eventType, (message) => {
        this.emit(message);
      });
    });
  }

  // 处理WebSocket断开
  private handleWebSocketDisconnect(): void {
    logger.warn('[WebSocket Manager] WebSocket断开，尝试重连', 'WebSocket');

    if (this.retryCount < this.maxRetries) {
      this.retryCount++;

      setTimeout(async () => {
        try {
          await this.connect();
        } catch (error) {
          logger.error('[WebSocket Manager] 重连失败', 'WebSocket', error);
        }
      }, 2000 * this.retryCount); // 指数退避

    } else {
      logger.warn('[WebSocket Manager] 达到最大重试次数，使用降级方案', 'WebSocket');
      this.connectFallback();
    }
  }

  // 清理所有事件绑定
  private unbindAllEvents(): void {
    // 这里可以添加清理逻辑
    // 由于我们的实现是重新绑定，暂时不需要显式清理
  }

  // 断开连接
  disconnect(): void {
    this._isConnecting = false;
    this.retryCount = 0;

    if (this.currentMode === ConnectionMode.WEBSOCKET) {
      enhancedWebSocketService.disconnect();
    } else if (this.currentMode === ConnectionMode.FALLBACK) {
      webSocketFallback.disconnect();
    }

    this.currentMode = ConnectionMode.OFFLINE;

    this.emit({
      type: 'connection_closed',
      payload: {
        code: 1000,
        reason: 'Manual disconnect',
        mode: 'offline'
      },
      timestamp: new Date().toISOString()
    });
  }

  // 发送消息
  send(message: any): boolean {
    if (this.currentMode === ConnectionMode.WEBSOCKET) {
      return enhancedWebSocketService.send(message);
    } else if (this.currentMode === ConnectionMode.FALLBACK) {
      webSocketFallback.send(message);
      return true;
    }

    logger.warn('[WebSocket Manager] 无可用连接，消息发送失败', 'WebSocket');
    return false;
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

  off(eventType: string, handler: WebSocketEventHandler): void {
    const handlers = this.eventHandlers.get(eventType);
    if (handlers) {
      handlers.delete(handler);
    }
  }

  private emit(message: any): void {
    const handlers = this.eventHandlers.get(message.type);
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(message);
        } catch (error) {
          logger.error('[WebSocket Manager] Event handler error:', 'WebSocket', error);
        }
      });
    }
  }

  // 获取连接状态
  get isConnected(): boolean {
    return this.currentMode !== ConnectionMode.OFFLINE;
  }

  get isConnecting(): boolean {
    return this._isConnecting;
  }

  get connectionMode(): ConnectionMode {
    return this.currentMode;
  }

  get connectionQuality(): number {
    if (this.currentMode === ConnectionMode.WEBSOCKET) {
      return enhancedWebSocketService.connectionQuality;
    } else if (this.currentMode === ConnectionMode.FALLBACK) {
      return 60; // 降级方案固定60分
    }
    return 0;
  }

  get connectionStatus(): any {
    if (this.currentMode === ConnectionMode.WEBSOCKET) {
      return enhancedWebSocketService.connectionStatus;
    } else if (this.currentMode === ConnectionMode.FALLBACK) {
      return {
        state: 'connected',
        quality: 60,
        metrics: { totalConnections: 1, successfulConnections: 1 },
        reconnectStats: { attempts: 0, maxAttempts: 0, nextRetryDelay: 0 }
      };
    }
    return {
      state: 'disconnected',
      quality: 0,
      metrics: {},
      reconnectStats: { attempts: 0, maxAttempts: 0, nextRetryDelay: 0 }
    };
  }

  // 手动刷新连接
  async refreshConnection(): Promise<void> {
    this.disconnect();
    await this.connect();
  }

  // 获取可用功能
  getAvailableFeatures(): string[] {
    const baseFeatures = ['基础消息发送', '连接状态监控'];

    if (this.currentMode === ConnectionMode.WEBSOCKET) {
      return [
        ...baseFeatures,
        '实时双向通信',
        '连接质量监控',
        '智能重连机制',
        '状态同步'
      ];
    } else if (this.currentMode === ConnectionMode.FALLBACK) {
      return [
        ...baseFeatures,
        '模拟数据更新',
        '离线模式支持',
        '基础交互功能'
      ];
    }

    return ['离线模式'];
  }

  // 清理资源
  destroy(): void {
    this.disconnect();
    this.eventHandlers.clear();
    enhancedWebSocketService.destroy();
    webSocketFallback.destroy();
  }
}

// 创建全局实例
export const webSocketManager = new WebSocketManager();
export default webSocketManager;

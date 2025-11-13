/**
 * 增强版 WebSocket Hook
 * 提供更好的状态管理和错误处理
 */

import { useEffect, useRef, useCallback, useState } from 'react';
import { enhancedWebSocketService } from '@services/websocketEnhanced';
import { connectionManager, ConnectionState } from '@utils/connectionManager';
import { useAppStore } from '@stores/index';

interface UseWebSocketOptions {
  autoConnect?: boolean;
  reconnectOnNetworkChange?: boolean;
  showConnectionNotifications?: boolean;
  maxRetries?: number;
}

interface ConnectionStatus {
  state: ConnectionState;
  quality: number;
  metrics: any;
  reconnectStats: any;
}

export const useWebSocketEnhanced = (options: UseWebSocketOptions = {}) => {
  const {
    autoConnect = true,
    reconnectOnNetworkChange = true,
    showConnectionNotifications = true,
    maxRetries = 10
  } = options;

  const {
    updateRealtimeData,
    addNotification,
    setLoading,
    setGlobalLoading
  } = useAppStore();

  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    state: ConnectionState.DISCONNECTED,
    quality: 0,
    metrics: {},
    reconnectStats: {}
  });

  const handlersRef = useRef<Map<string, (message: any) => void>>(new Map());
  const retryCountRef = useRef(0);
  const lastConnectedRef = useRef<boolean>(false);

  // 连接WebSocket
  const connect = useCallback(async () => {
    try {
      setGlobalLoading(true);
      setLoading('websocket', true);

      await enhancedWebSocketService.connect();
      retryCountRef.current = 0; // 重置重试计数

      if (showConnectionNotifications) {
        addNotification({
          type: 'success',
          title: '连接成功',
          message: 'WebSocket连接已建立，实时数据更新已启用',
        });
      }
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      retryCountRef.current++;

      // 智能重试逻辑
      if (retryCountRef.current < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, retryCountRef.current - 1), 10000);

        setTimeout(() => {
          if (autoConnect) {
            connect();
          }
        }, delay);
      }

      if (showConnectionNotifications) {
        addNotification({
          type: 'error',
          title: '连接失败',
          message: `无法建立WebSocket连接，将使用轮询模式 (${retryCountRef.current}/${maxRetries})`,
        });
      }
    } finally {
      setGlobalLoading(false);
      setLoading('websocket', false);
    }
  }, [addNotification, setGlobalLoading, setLoading, autoConnect, showConnectionNotifications, maxRetries]);

  // 断开连接
  const disconnect = useCallback(() => {
    enhancedWebSocketService.disconnect();
    retryCountRef.current = 0;

    if (showConnectionNotifications) {
      addNotification({
        type: 'info',
        title: '连接断开',
        message: 'WebSocket连接已断开',
      });
    }
  }, [addNotification, showConnectionNotifications]);

  // 发送消息
  const send = useCallback((message: any): boolean => {
    return enhancedWebSocketService.send(message);
  }, []);

  // 注册事件处理器
  const on = useCallback((eventType: string, handler: (message: any) => void) => {
    handlersRef.current.set(eventType, handler);
    return enhancedWebSocketService.on(eventType, handler);
  }, []);

  // 移除事件处理器
  const off = useCallback((eventType: string, handler: (message: any) => void) => {
    handlersRef.current.delete(eventType);
    enhancedWebSocketService.off(eventType, handler);
  }, []);

  // 一次性事件处理器
  const once = useCallback((eventType: string, handler: (message: any) => void) => {
    enhancedWebSocketService.once(eventType, handler);
  }, []);

  // 网络状态变化监听
  useEffect(() => {
    if (!reconnectOnNetworkChange) return;

    const handleOnline = () => {
      if (!enhancedWebSocketService.isConnected && autoConnect) {
        console.log('[WebSocket] Network restored, reconnecting...');
        connect();
      }
    };

    const handleOffline = () => {
      console.log('[WebSocket] Network lost');
    };

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [reconnectOnNetworkChange, autoConnect, connect]);

  // 自动连接
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      if (autoConnect) {
        disconnect();
      }
    };
  }, [autoConnect, connect, disconnect]);

  // 连接状态监听
  useEffect(() => {
    const unsubscribeStateChange = connectionManager.onStateChange((state) => {
      const isConnected = state === ConnectionState.CONNECTED;

      // 只在连接状态真正改变时更新UI
      if (lastConnectedRef.current !== isConnected) {
        lastConnectedRef.current = isConnected;
        setLoading('websocket', !isConnected);
      }

      setConnectionStatus({
        state,
        quality: enhancedWebSocketService.connectionQuality,
        metrics: enhancedWebSocketService.connectionMetrics,
        reconnectStats: enhancedWebSocketService.reconnectStats
      });
    });

    return unsubscribeStateChange;
  }, [setLoading]);

  // 默认事件处理器
  useEffect(() => {
    // 状态更新处理器
    const unsubscribeStateUpdate = enhancedWebSocketService.on('state_update', (message) => {
      const { langGraphState } = message.payload;
      if (langGraphState) {
        updateRealtimeData({ langGraphState });

        // 减少通知频率，只在重要状态变化时通知
        if (showConnectionNotifications && langGraphState.status === 'completed') {
          addNotification({
            type: 'success',
            title: '任务完成',
            message: 'LangGraph执行已完成',
            duration: 3000
          });
        }
      }
    });

    // 记忆更新处理器
    const unsubscribeMemoryUpdate = enhancedWebSocketService.on('memory_update', (message) => {
      const { memoryNetwork } = message.payload;
      if (memoryNetwork) {
        updateRealtimeData({ memoryNetwork });
      }
    });

    // 消息更新处理器
    const unsubscribeMessageUpdate = enhancedWebSocketService.on('message_update', (message) => {
      // 只记录重要消息
      if (message.payload.level === 'important') {
        console.log('重要实时消息:', message.payload);
      }
    });

    // 错误处理器 - 增强错误处理
    const unsubscribeError = enhancedWebSocketService.on('error', (message) => {
      const { error, attempt, nextRetryIn } = message.payload;

      // 只对关键错误显示通知
      if (typeof error === 'string' && error.includes('Max reconnection')) {
        addNotification({
          type: 'error',
          title: '连接失败',
          message: '已达到最大重连次数，请刷新页面重试',
          duration: 0, // 不自动消失
          actions: [
            {
              label: '刷新',
              action: 'refresh'
            }
          ]
        });
      } else if (showConnectionNotifications && attempt && attempt > 3) {
        addNotification({
          type: 'warning',
          title: '连接不稳定',
          message: `正在尝试重连 (${attempt})，预计 ${Math.round(nextRetryIn / 1000)}秒后重试`,
          duration: 5000
        });
      }
    });

    // 连接质量更新处理器
    const unsubscribeQualityUpdate = enhancedWebSocketService.on('connection_quality_update', (message) => {
      const { quality, state } = message.payload;

      // 只在质量显著下降时通知
      if (showConnectionNotifications && quality < 50 && state === ConnectionState.CONNECTED) {
        addNotification({
          type: 'warning',
          title: '连接质量下降',
          message: `当前连接质量: ${quality}%，可能会影响实时数据更新`,
          duration: 5000
        });
      }
    });

    return () => {
      unsubscribeStateUpdate();
      unsubscribeMemoryUpdate();
      unsubscribeMessageUpdate();
      unsubscribeError();
      unsubscribeQualityUpdate();
    };
  }, [updateRealtimeData, addNotification, showConnectionNotifications]);

  return {
    // 连接方法
    connect,
    disconnect,
    send,
    on,
    off,
    once,

    // 连接状态
    isConnected: enhancedWebSocketService.isConnected,
    isConnecting: enhancedWebSocketService.isConnecting,
    connectionState: enhancedWebSocketService.connectionState,
    connectionStatus,
    readyState: enhancedWebSocketService.readyState,

    // 连接质量
    connectionQuality: enhancedWebSocketService.connectionQuality,
    connectionMetrics: enhancedWebSocketService.connectionMetrics,
    reconnectStats: enhancedWebSocketService.reconnectStats,

    // 手动刷新连接
    refreshConnection: () => {
      disconnect();
      setTimeout(connect, 1000);
    }
  };
};

// 专门用于聊天实时更新的增强hook
export const useChatWebSocketEnhanced = (sessionId: string | null) => {
  const {
    updateRealtimeData,
    addNotification
  } = useAppStore();

  const {
    connect,
    disconnect,
    send,
    isConnected,
    connectionQuality
  } = useWebSocketEnhanced({
    autoConnect: !!sessionId,
    showConnectionNotifications: false // 聊天场景减少通知干扰
  });

  // 订阅会话状态更新
  const subscribeToSession = useCallback((sessionId: string) => {
    const success = send({
      type: 'subscribe',
      payload: {
        action: 'subscribe_session',
        session_id: sessionId,
      },
    });

    if (!success) {
      console.warn('[ChatWebSocket] Failed to subscribe to session:', sessionId);
    }

    return success;
  }, [send]);

  // 取消订阅会话
  const unsubscribeFromSession = useCallback((sessionId: string) => {
    return send({
      type: 'unsubscribe',
      payload: {
        action: 'unsubscribe_session',
        session_id: sessionId,
      },
    });
  }, [send]);

  // 当sessionId变化时，重新订阅
  useEffect(() => {
    if (sessionId && isConnected) {
      subscribeToSession(sessionId);
    }

    return () => {
      if (sessionId) {
        unsubscribeFromSession(sessionId);
      }
    };
  }, [sessionId, isConnected, subscribeToSession, unsubscribeFromSession]);

  return {
    isConnected,
    connectionQuality,
    subscribeToSession,
    unsubscribeFromSession,
  };
};
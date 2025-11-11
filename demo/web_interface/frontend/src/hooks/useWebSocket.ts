import { useEffect, useRef, useCallback } from 'react';
import { webSocketService, WebSocketMessage } from '@services/index';
import { useAppStore } from '@stores/index';

export const useWebSocket = (autoConnect = true) => {
  const {
    updateRealtimeData,
    addNotification,
    setLoading,
    setGlobalLoading
  } = useAppStore();

  const handlersRef = useRef<Map<string, (message: WebSocketMessage) => void>>(new Map());

  // 连接WebSocket
  const connect = useCallback(async () => {
    try {
      setGlobalLoading(true);
      await webSocketService.connect();
      addNotification({
        type: 'success',
        title: '连接成功',
        message: 'WebSocket连接已建立，实时数据更新已启用',
      });
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      addNotification({
        type: 'error',
        title: '连接失败',
        message: '无法建立WebSocket连接，将使用轮询模式获取数据',
      });
    } finally {
      setGlobalLoading(false);
    }
  }, [addNotification, setGlobalLoading]);

  // 断开连接
  const disconnect = useCallback(() => {
    webSocketService.disconnect();
    addNotification({
      type: 'info',
      title: '连接断开',
      message: 'WebSocket连接已断开',
    });
  }, [addNotification]);

  // 发送消息
  const send = useCallback((message: Omit<WebSocketMessage, 'timestamp'>) => {
    webSocketService.send(message);
  }, []);

  // 注册事件处理器
  const on = useCallback((eventType: string, handler: (message: WebSocketMessage) => void) => {
    handlersRef.current.set(eventType, handler);
    return webSocketService.on(eventType, handler);
  }, []);

  // 移除事件处理器
  const off = useCallback((eventType: string, handler: (message: WebSocketMessage) => void) => {
    handlersRef.current.delete(eventType);
    webSocketService.off(eventType, handler);
  }, []);

  // 一次性事件处理器
  const once = useCallback((eventType: string, handler: (message: WebSocketMessage) => void) => {
    webSocketService.once(eventType, handler);
  }, []);

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

  // 默认事件处理器
  useEffect(() => {
    // 状态更新处理器
    const unsubscribeStateUpdate = webSocketService.on('state_update', (message) => {
      const { langGraphState } = message.payload;
      if (langGraphState) {
        updateRealtimeData({ langGraphState });

        addNotification({
          type: 'info',
          title: '状态更新',
          message: 'LangGraph执行状态已更新',
        });
      }
    });

    // 记忆更新处理器
    const unsubscribeMemoryUpdate = webSocketService.on('memory_update', (message) => {
      const { memoryNetwork } = message.payload;
      if (memoryNetwork) {
        updateRealtimeData({ memoryNetwork });
      }
    });

    // 消息更新处理器
    const unsubscribeMessageUpdate = webSocketService.on('message_update', (message) => {
      // 可以在这里处理实时消息更新
      console.log('实时消息更新:', message.payload);
    });

    // 错误处理器
    const unsubscribeError = webSocketService.on('error', (message) => {
      addNotification({
        type: 'error',
        title: '实时更新错误',
        message: message.payload.error || '发生未知错误',
      });
    });

    // 连接状态处理器
    const unsubscribeConnectionOpened = webSocketService.on('connection_opened', () => {
      setLoading('websocket', false);
    });

    const unsubscribeConnectionClosed = () => {
      setLoading('websocket', true);
    };

    return () => {
      unsubscribeStateUpdate();
      unsubscribeMemoryUpdate();
      unsubscribeMessageUpdate();
      unsubscribeError();
      unsubscribeConnectionOpened();
      unsubscribeConnectionClosed();
    };
  }, [updateRealtimeData, addNotification, setLoading]);

  return {
    connect,
    disconnect,
    send,
    on,
    off,
    once,
    isConnected: webSocketService.isConnected,
    isConnecting: webSocketService.isConnecting,
    readyState: webSocketService.readyState,
  };
};

// 专门用于聊天实时更新的hook
export const useChatWebSocket = (sessionId: string | null) => {
  const {
    updateRealtimeData,
    addNotification
  } = useAppStore();

  const {
    connect,
    disconnect,
    send,
    isConnected
  } = useWebSocket(!!sessionId);

  // 订阅会话状态更新
  const subscribeToSession = useCallback((sessionId: string) => {
    send({
      type: 'subscribe',
      payload: {
        action: 'subscribe_session',
        session_id: sessionId,
      },
    });
  }, [send]);

  // 取消订阅会话
  const unsubscribeFromSession = useCallback((sessionId: string) => {
    send({
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
    subscribeToSession,
    unsubscribeFromSession,
  };
};

// 用于数据可视化的WebSocket hook
export const useVisualizationWebSocket = () => {
  const { updateRealtimeData } = useAppStore();

  // 注册专门的可视化事件处理器
  const onVisualizationUpdate = useCallback((callback: (data: any) => void) => {
    return webSocketService.on('visualization_update', (message) => {
      const { type, data } = message.payload;
      callback({ type, data });
    });
  }, []);

  // 请求可视化数据
  const requestVisualizationData = useCallback((visualizationType: string, params?: any) => {
    webSocketService.send({
      type: 'visualization_request',
      payload: {
        visualization_type: visualizationType,
        params: params || {},
      },
    });
  }, []);

  return {
    onVisualizationUpdate,
    requestVisualizationData,
    isConnected: webSocketService.isConnected,
  };
};
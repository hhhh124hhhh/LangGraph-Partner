/**
 * WebSocket Manager Hook
 * 提供WebSocket管理的React Hook接口
 */

import { useCallback, useState, useRef, useEffect, useSyncExternalStore, useDebugValue } from 'react';
import { webSocketManager, ConnectionMode } from '@services/websocketManager';
import { useAppStore } from '@stores/index';

export interface UseWebSocketManagerOptions {
  autoConnect?: boolean;
  showConnectionNotifications?: boolean;
  onConnectionOpen?: (mode: ConnectionMode) => void;
  onConnectionClose?: (mode: ConnectionMode) => void;
  onConnectionError?: (error: any) => void;
  onMessage?: (message: any) => void;
}

export interface UseChatWebSocketManagerOptions extends UseWebSocketManagerOptions {
  // 聊天特定的选项
}

export const useWebSocketManager = (options: UseWebSocketManagerOptions = {}) => {
  const {
    autoConnect = true,
    showConnectionNotifications = true,
    onConnectionOpen,
    onConnectionClose,
    onConnectionError,
    onMessage
  } = options;

  const {
    addNotification
  } = useAppStore();

  const handlersRef = useRef<Map<string, (message: any) => void>>(new Map());
  const isInitialized = useRef(false);

  // 使用React状态来跟踪WebSocket连接状态，确保组件能够响应状态变化
  const [isConnected, setIsConnected] = useState(webSocketManager.isConnected);
  const [isConnecting, setIsConnecting] = useState(webSocketManager.isConnecting);
  const [connectionMode, setConnectionMode] = useState(webSocketManager.connectionMode);
  const [connectionQuality, setConnectionQuality] = useState(webSocketManager.connectionQuality);
  const [availableFeatures, setAvailableFeatures] = useState(webSocketManager.getAvailableFeatures());

  // 连接WebSocket
  const connect = useCallback(async () => {
    try {
      if (showConnectionNotifications) {
        addNotification({
          type: 'info',
          title: '连接中',
          message: '正在连接到服务器...',
          duration: 3000
        });
      }

      await webSocketManager.connect();

      if (showConnectionNotifications) {
        addNotification({
          type: 'success',
          title: '连接成功',
          message: `已连接到服务器 (${webSocketManager.connectionMode})`,
          duration: 3000
        });
      }

      if (onConnectionOpen) {
        onConnectionOpen(webSocketManager.connectionMode);
      }

    } catch (error) {
      console.error('[WebSocket Manager Hook] 连接失败:', error);

      if (showConnectionNotifications) {
        addNotification({
          type: 'error',
          title: '连接失败',
          message: '无法连接到服务器，将使用离线模式',
          duration: 5000
        });
      }

      if (onConnectionError) {
        onConnectionError(error);
      }
    }
  }, [addNotification, showConnectionNotifications, onConnectionOpen, onConnectionError]);

  // 断开连接
  const disconnect = useCallback(() => {
    webSocketManager.disconnect();

    if (showConnectionNotifications) {
      addNotification({
        type: 'info',
        title: '连接断开',
        message: '与服务器的连接已断开',
        duration: 3000
      });
    }

    if (onConnectionClose) {
      onConnectionClose(webSocketManager.connectionMode);
    }
  }, [addNotification, showConnectionNotifications, onConnectionClose]);

  // 发送消息
  const send = useCallback((message: any) => {
    const success = webSocketManager.send(message);

    if (!success && showConnectionNotifications) {
      addNotification({
        type: 'warning',
        title: '发送失败',
        message: '消息发送失败，请检查连接状态',
        duration: 3000
      });
    }

    return success;
  }, [addNotification, showConnectionNotifications]);

  // 注册事件处理器
  const on = useCallback((eventType: string, handler: (message: any) => void) => {
    handlersRef.current.set(eventType, handler);
    return webSocketManager.on(eventType, handler);
  }, []);

  // 移除事件处理器
  const off = useCallback((eventType: string, handler: (message: any) => void) => {
    handlersRef.current.delete(eventType);
    webSocketManager.off(eventType, handler);
  }, []);

  // 一次性事件处理器
  const once = useCallback((eventType: string, handler: (message: any) => void) => {
    webSocketManager.once(eventType, handler);
  }, []);

  // 手动刷新连接
  const refreshConnection = useCallback(async () => {
    if (showConnectionNotifications) {
      addNotification({
        type: 'info',
        title: '重新连接',
        message: '正在重新连接到服务器...',
        duration: 3000
      });
    }

    await webSocketManager.refreshConnection();
  }, [addNotification, showConnectionNotifications]);

  // 自动连接
  useEffect(() => {
    if (autoConnect && !isInitialized.current) {
      isInitialized.current = true;
      connect();
    }

    return () => {
      if (autoConnect && isInitialized.current) {
        disconnect();
        isInitialized.current = false;
      }
    };
  }, [autoConnect, connect, disconnect]);

  // 默认事件处理器
  useEffect(() => {
    // 连接状态处理器
    const unsubscribeConnectionOpened = webSocketManager.on('connection_opened', (message) => {
      console.log('[WebSocket Manager Hook] 连接已建立:', message);
      console.log('[WebSocket Manager Hook] 连接状态:', webSocketManager.isConnected);
      console.log('[WebSocket Manager Hook] 连接模式:', webSocketManager.connectionMode);
      console.log('[WebSocket Manager Hook] 可用功能:', webSocketManager.getAvailableFeatures());
      setIsConnected(true);
      setIsConnecting(false);
      setConnectionMode(webSocketManager.connectionMode);
      setConnectionQuality(webSocketManager.connectionQuality);
      setAvailableFeatures(webSocketManager.getAvailableFeatures());
    });

    const unsubscribeConnectionClosed = webSocketManager.on('connection_closed', (message) => {
      console.log('[WebSocket Manager Hook] 连接已关闭:', message);
      setIsConnected(false);
      setIsConnecting(false);
      setConnectionMode(webSocketManager.connectionMode);
      setConnectionQuality(webSocketManager.connectionQuality);
      setAvailableFeatures(webSocketManager.getAvailableFeatures());
    });

    const unsubscribeConnectionError = webSocketManager.on('connection_error', (message) => {
      console.log('[WebSocket Manager Hook] 连接错误:', message);
      setIsConnected(false);
      setIsConnecting(false);
      setConnectionMode(webSocketManager.connectionMode);
      setConnectionQuality(webSocketManager.connectionQuality);
      setAvailableFeatures(webSocketManager.getAvailableFeatures());
    });

    // 监听所有可能的消息类型
    const messageTypes = ['message_response', 'message_update', 'state_update', 'memory_update', 'error'];
    const unsubscribeFunctions = messageTypes.map(type => {
      return webSocketManager.on(type, (message) => {
        if (onMessage) {
          onMessage(message);
        }
      });
    });

    return () => {
      unsubscribeConnectionOpened();
      unsubscribeConnectionClosed();
      unsubscribeConnectionError();
      unsubscribeFunctions.forEach(unsubscribe => unsubscribe());
    };
  }, [onMessage]);

  return {
    // 连接方法
    connect,
    disconnect,
    send,
    on,
    off,
    once,
    refreshConnection,

    // 连接状态
    isConnected,
    isConnecting,
    connectionMode,
    connectionQuality,
    connectionStatus: webSocketManager.connectionStatus,
    
    // 功能信息
    availableFeatures,

    // 连接模式文本
    getConnectionModeText: () => {
      switch (connectionMode) {
        case ConnectionMode.WEBSOCKET:
          return 'WebSocket实时连接';
        case ConnectionMode.FALLBACK:
          return '模拟连接';
        case ConnectionMode.OFFLINE:
          return '离线模式';
        default:
          return '未知模式';
      }
    },

    // 获取连接模式图标
    getConnectionModeIcon: () => {
      switch (connectionMode) {
        case ConnectionMode.WEBSOCKET:
          return '🟢';
        case ConnectionMode.FALLBACK:
          return '🟡';
        case ConnectionMode.OFFLINE:
          return '🔴';
        default:
          return '⚪';
      }
    }
  };
};

// 专门用于聊天的WebSocket Hook
export const useChatWebSocketManager = (sessionId: string | null, options: UseChatWebSocketManagerOptions = {}) => {
  const {
    connect,
    disconnect,
    isConnected,
    connectionMode,
    send,
    on,
    off,
    availableFeatures
  } = useWebSocketManager({
    autoConnect: !!sessionId,
    showConnectionNotifications: true,
    ...options
  });

  // 当sessionId从null变为有效值时，自动连接
  useEffect(() => {
    if (sessionId && !isConnected) {
      connect();
    } else if (!sessionId && isConnected) {
      disconnect();
    }
  }, [sessionId, isConnected, connect, disconnect]);

  // 订阅会话
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

  // 发送聊天消息
  const sendChatMessage = useCallback((content: string, attachments?: any[]) => {
    return send({
      type: 'message',
      payload: {
        content,
        attachments: attachments || [],
        session_id: sessionId
      },
    });
  }, [send, sessionId]);

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

  console.log('[Chat WebSocket Manager] isConnected:', isConnected);
  console.log('[Chat WebSocket Manager] availableFeatures:', availableFeatures);
  console.log('[Chat WebSocket Manager] canSendMessages:', isConnected && (availableFeatures.includes('实时双向通信') || availableFeatures.includes('模拟数据更新')));
  
  return {
    isConnected,
    connectionMode,
    sendChatMessage,
    availableFeatures,
    canSendMessages: isConnected && (availableFeatures.includes('实时双向通信') || availableFeatures.includes('模拟数据更新')),
    on,
    off
  };
};

export default useWebSocketManager;
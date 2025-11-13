/**
 * WebSocket 连接状态管理器
 * 提供健壮的连接状态管理和监控
 */

export enum ConnectionState {
  DISCONNECTED = 'disconnected',
  CONNECTING = 'connecting',
  CONNECTED = 'connected',
  RECONNECTING = 'reconnecting',
  ERROR = 'error'
}

export interface ConnectionMetrics {
  totalConnections: number;
  successfulConnections: number;
  failedConnections: number;
  totalReconnections: number;
  averageReconnectTime: number;
  lastConnectedAt?: Date;
  lastDisconnectedAt?: Date;
  connectionUptime: number;
}

export interface ConnectionConfig {
  maxReconnectAttempts: number;
  baseReconnectDelay: number;
  maxReconnectDelay: number;
  reconnectBackoffFactor: number;
  heartbeatInterval: number;
  connectionTimeout: number;
  healthCheckInterval: number;
}

class ConnectionManager {
  private state: ConnectionState = ConnectionState.DISCONNECTED;
  private config: ConnectionConfig;
  private metrics: ConnectionMetrics;
  private stateChangeListeners: Set<(state: ConnectionState) => void> = new Set();
  private reconnectStartTime: number = 0;
  private connectionStartTime: number = 0;
  private healthCheckTimer?: NodeJS.Timeout;
  private connectionTimeoutTimer?: NodeJS.Timeout;

  constructor(config?: Partial<ConnectionConfig>) {
    this.config = {
      maxReconnectAttempts: 10,
      baseReconnectDelay: 1000,
      maxReconnectDelay: 30000,
      reconnectBackoffFactor: 2,
      heartbeatInterval: 30000,
      connectionTimeout: 10000,
      healthCheckInterval: 5000,
      ...config
    };

    this.metrics = {
      totalConnections: 0,
      successfulConnections: 0,
      failedConnections: 0,
      totalReconnections: 0,
      averageReconnectTime: 0,
      connectionUptime: 0
    };
  }

  // 获取当前连接状态
  getState(): ConnectionState {
    return this.state;
  }

  // 设置连接状态
  setState(newState: ConnectionState): void {
    const oldState = this.state;
    this.state = newState;

    // 更新指标
    this.updateMetrics(oldState, newState);

    // 通知状态变更监听器
    this.notifyStateChange(newState);
  }

  // 监听状态变更
  onStateChange(listener: (state: ConnectionState) => void): () => void {
    this.stateChangeListeners.add(listener);
    return () => this.stateChangeListeners.delete(listener);
  }

  // 计算重连延迟（指数退避）
  calculateReconnectDelay(attemptNumber: number): number {
    const delay = Math.min(
      this.config.baseReconnectDelay * Math.pow(this.config.reconnectBackoffFactor, attemptNumber - 1),
      this.config.maxReconnectDelay
    );

    // 添加随机抖动，避免同时重连
    const jitter = Math.random() * 0.3 * delay;
    return Math.floor(delay + jitter);
  }

  // 开始连接计时
  startConnectionTimer(): void {
    this.connectionStartTime = Date.now();

    // 设置连接超时
    this.connectionTimeoutTimer = setTimeout(() => {
      if (this.state === ConnectionState.CONNECTING || this.state === ConnectionState.RECONNECTING) {
        this.setState(ConnectionState.ERROR);
      }
    }, this.config.connectionTimeout);
  }

  // 开始重连计时
  startReconnectTimer(): void {
    this.reconnectStartTime = Date.now();
  }

  // 连接成功
  onConnectionSuccess(): void {
    if (this.connectionTimeoutTimer) {
      clearTimeout(this.connectionTimeoutTimer);
      this.connectionTimeoutTimer = undefined;
    }

    this.metrics.successfulConnections++;
    this.metrics.lastConnectedAt = new Date();

    if (this.state === ConnectionState.RECONNECTING) {
      const reconnectTime = Date.now() - this.reconnectStartTime;
      this.updateAverageReconnectTime(reconnectTime);
    }

    this.setState(ConnectionState.CONNECTED);
    this.startHealthCheck();
  }

  // 连接失败
  onConnectionFailure(): void {
    if (this.connectionTimeoutTimer) {
      clearTimeout(this.connectionTimeoutTimer);
      this.connectionTimeoutTimer = undefined;
    }

    this.metrics.failedConnections++;
    this.metrics.lastDisconnectedAt = new Date();
    this.setState(ConnectionState.ERROR);
  }

  // 连接断开
  onDisconnection(): void {
    this.metrics.lastDisconnectedAt = new Date();
    this.setState(ConnectionState.DISCONNECTED);
    this.stopHealthCheck();
  }

  // 开始重连
  onReconnectStart(): void {
    this.metrics.totalReconnections++;
    this.startReconnectTimer();
    this.setState(ConnectionState.RECONNECTING);
  }

  // 收到pong响应
  onPongReceived(): void {
    // 更新连接质量，表示心跳正常
    if (this.state === ConnectionState.CONNECTED) {
      // 可以在这里添加心跳延迟统计
      console.debug('[ConnectionManager] Pong received, connection healthy');
    }
  }

  // 开始健康检查
  private startHealthCheck(): void {
    this.stopHealthCheck();

    this.healthCheckTimer = setInterval(() => {
      this.updateConnectionUptime();
    }, this.config.healthCheckInterval);
  }

  // 停止健康检查
  private stopHealthCheck(): void {
    if (this.healthCheckTimer) {
      clearInterval(this.healthCheckTimer);
      this.healthCheckTimer = undefined;
    }
  }

  // 更新连接运行时间
  private updateConnectionUptime(): void {
    if (this.state === ConnectionState.CONNECTED && this.metrics.lastConnectedAt) {
      this.metrics.connectionUptime = Date.now() - this.metrics.lastConnectedAt.getTime();
    }
  }

  // 更新平均重连时间
  private updateAverageReconnectTime(reconnectTime: number): void {
    const totalReconnects = this.metrics.totalReconnections;
    const currentAverage = this.metrics.averageReconnectTime;

    this.metrics.averageReconnectTime =
      (currentAverage * (totalReconnects - 1) + reconnectTime) / totalReconnects;
  }

  // 更新指标
  private updateMetrics(oldState: ConnectionState, newState: ConnectionState): void {
    if (oldState === ConnectionState.DISCONNECTED &&
        (newState === ConnectionState.CONNECTING || newState === ConnectionState.RECONNECTING)) {
      this.metrics.totalConnections++;
    }
  }

  // 通知状态变更
  private notifyStateChange(state: ConnectionState): void {
    this.stateChangeListeners.forEach(listener => {
      try {
        listener(state);
      } catch (error) {
        console.error('[ConnectionManager] State change listener error:', error);
      }
    });
  }

  // 获取连接指标
  getMetrics(): ConnectionMetrics {
    this.updateConnectionUptime(); // 更新运行时间
    return { ...this.metrics };
  }

  // 重置指标
  resetMetrics(): void {
    this.metrics = {
      totalConnections: 0,
      successfulConnections: 0,
      failedConnections: 0,
      totalReconnections: 0,
      averageReconnectTime: 0,
      connectionUptime: 0
    };
  }

  // 获取连接质量分数 (0-100)
  getConnectionQuality(): number {
    const metrics = this.metrics;

    if (metrics.totalConnections === 0) return 100;

    const successRate = metrics.successfulConnections / metrics.totalConnections;
    const avgReconnectTime = Math.min(metrics.averageReconnectTime / 1000, 10); // 10秒为满分
    const reconnectScore = Math.max(0, 10 - avgReconnectTime) / 10;

    return Math.round((successRate * 0.7 + reconnectScore * 0.3) * 100);
  }

  // 获取配置
  getConfig(): ConnectionConfig {
    return { ...this.config };
  }

  // 更新配置
  updateConfig(newConfig: Partial<ConnectionConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  // 清理资源
  destroy(): void {
    this.stopHealthCheck();
    if (this.connectionTimeoutTimer) {
      clearTimeout(this.connectionTimeoutTimer);
      this.connectionTimeoutTimer = undefined;
    }
    this.stateChangeListeners.clear();
  }
}

// 创建单例实例
export const connectionManager = new ConnectionManager();
export default connectionManager;
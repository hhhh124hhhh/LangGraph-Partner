/**
 * 优化的日志工具
 * 提供分级日志、性能监控和错误追踪
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  SILENT = 4
}

export interface LogEntry {
  timestamp: number;
  level: LogLevel;
  message: string;
  data?: any;
  module?: string;
  userId?: string;
  sessionId?: string;
}

interface LoggerConfig {
  level: LogLevel;
  enableConsole: boolean;
  enableStorage: boolean;
  maxStorageEntries: number;
  enablePerformanceLogging: boolean;
}

class Logger {
  private config: LoggerConfig;
  private logs: LogEntry[] = [];
  private sessionId: string;

  constructor(config: Partial<LoggerConfig> = {}) {
    this.sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    this.config = {
      level: process.env.NODE_ENV === 'development' ? LogLevel.DEBUG : LogLevel.WARN,
      enableConsole: true,
      enableStorage: true,
      maxStorageEntries: 1000,
      enablePerformanceLogging: true,
      ...config
    };

    // 初始化时加载存储的日志
    this.loadStoredLogs();

    // 监听页面卸载，保存日志
    window.addEventListener('beforeunload', () => {
      this.saveLogs();
    });
  }

  private loadStoredLogs(): void {
    try {
      const stored = localStorage.getItem('app_logs');
      if (stored) {
        this.logs = JSON.parse(stored);
        // 限制日志数量
        if (this.logs.length > this.config.maxStorageEntries) {
          this.logs = this.logs.slice(-this.config.maxStorageEntries);
        }
      }
    } catch (error) {
      console.warn('[Logger] 无法加载存储的日志:', error);
    }
  }

  private saveLogs(): void {
    if (!this.config.enableStorage) return;

    try {
      localStorage.setItem('app_logs', JSON.stringify(this.logs));
    } catch (error) {
      console.warn('[Logger] 无法保存日志:', error);
      // 如果存储空间不足，清理一些旧日志
      try {
        this.logs = this.logs.slice(-500);
        localStorage.setItem('app_logs', JSON.stringify(this.logs));
      } catch (e) {
        console.warn('[Logger] 清理日志后仍然无法保存:', e);
      }
    }
  }

  private shouldLog(level: LogLevel): boolean {
    return level >= this.config.level;
  }

  private createLogEntry(level: LogLevel, message: string, data?: any, module?: string): LogEntry {
    return {
      timestamp: Date.now(),
      level,
      message,
      data,
      module,
      sessionId: this.sessionId
    };
  }

  private log(entry: LogEntry): void {
    // 添加到内存
    this.logs.push(entry);

    // 限制内存中的日志数量
    if (this.logs.length > this.config.maxStorageEntries) {
      this.logs = this.logs.slice(-this.config.maxStorageEntries);
    }

    // 控制台输出
    if (this.config.enableConsole && this.shouldLog(entry.level)) {
      this.outputToConsole(entry);
    }

    // 定期保存到localStorage
    if (this.config.enableStorage && this.logs.length % 10 === 0) {
      this.saveLogs();
    }
  }

  private outputToConsole(entry: LogEntry): void {
    const time = new Date(entry.timestamp).toLocaleTimeString();
    const prefix = `[${time}][${entry.module || 'App'}]`;

    switch (entry.level) {
      case LogLevel.DEBUG:
        console.debug(prefix, entry.message, entry.data);
        break;
      case LogLevel.INFO:
        console.info(prefix, entry.message, entry.data);
        break;
      case LogLevel.WARN:
        console.warn(prefix, entry.message, entry.data);
        break;
      case LogLevel.ERROR:
        console.error(prefix, entry.message, entry.data);
        break;
    }
  }

  // 公共日志方法
  debug(message: string, data?: any, module?: string): void {
    const entry = this.createLogEntry(LogLevel.DEBUG, message, data, module);
    this.log(entry);
  }

  info(message: string, data?: any, module?: string): void {
    const entry = this.createLogEntry(LogLevel.INFO, message, data, module);
    this.log(entry);
  }

  warn(message: string, data?: any, module?: string): void {
    const entry = this.createLogEntry(LogLevel.WARN, message, data, module);
    this.log(entry);
  }

  error(message: string, error?: Error | any, module?: string): void {
    let data = error;
    if (error instanceof Error) {
      data = {
        name: error.name,
        message: error.message,
        stack: error.stack
      };
    }

    const entry = this.createLogEntry(LogLevel.ERROR, message, data, module);
    this.log(entry);
  }

  // 性能日志
  performance(operation: string, duration: number, data?: any): void {
    if (!this.config.enablePerformanceLogging) return;

    const message = `Performance: ${operation} took ${duration}ms`;
    const logData = {
      operation,
      duration,
      ...data
    };

    const level = duration > 1000 ? LogLevel.WARN : LogLevel.DEBUG;
    const entry = this.createLogEntry(level, message, logData, 'Performance');
    this.log(entry);
  }

  // 用户行为日志
  userAction(action: string, data?: any): void {
    const message = `User Action: ${action}`;
    const entry = this.createLogEntry(LogLevel.INFO, message, data, 'UserAction');
    this.log(entry);
  }

  // API请求日志
  apiRequest(method: string, url: string, status: number, duration: number, error?: any): void {
    const message = `API ${method} ${url} - ${status}`;
    const logData = {
      method,
      url,
      status,
      duration,
      error
    };

    const level = status >= 400 ? LogLevel.WARN : LogLevel.DEBUG;
    const entry = this.createLogEntry(level, message, logData, 'API');
    this.log(entry);
  }

  // WebSocket日志
  websocket(event: string, data?: any): void {
    const message = `WebSocket: ${event}`;
    const entry = this.createLogEntry(LogLevel.DEBUG, message, data, 'WebSocket');
    this.log(entry);
  }

  // 配置更新
  updateConfig(newConfig: Partial<LoggerConfig>): void {
    this.config = { ...this.config, ...newConfig };
  }

  // 获取日志
  getLogs(level?: LogLevel, module?: string, limit?: number): LogEntry[] {
    let filteredLogs = this.logs;

    if (level !== undefined) {
      filteredLogs = filteredLogs.filter(log => log.level >= level);
    }

    if (module) {
      filteredLogs = filteredLogs.filter(log => log.module === module);
    }

    if (limit) {
      filteredLogs = filteredLogs.slice(-limit);
    }

    return filteredLogs;
  }

  // 获取错误日志
  getErrorLogs(limit?: number): LogEntry[] {
    return this.getLogs(LogLevel.ERROR, undefined, limit);
  }

  // 获取性能日志
  getPerformanceLogs(limit?: number): LogEntry[] {
    return this.getLogs(LogLevel.DEBUG, 'Performance', limit);
  }

  // 清理日志
  clearLogs(): void {
    this.logs = [];
    if (this.config.enableStorage) {
      localStorage.removeItem('app_logs');
    }
  }

  // 导出日志
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  // 获取日志统计
  getStats(): {
    total: number;
    byLevel: Record<LogLevel, number>;
    byModule: Record<string, number>;
    timeRange: { earliest: number; latest: number };
  } {
    const stats = {
      total: this.logs.length,
      byLevel: {} as Record<LogLevel, number>,
      byModule: {} as Record<string, number>,
      timeRange: {
        earliest: this.logs[0]?.timestamp || Date.now(),
        latest: this.logs[this.logs.length - 1]?.timestamp || Date.now()
      }
    };

    // 初始化计数器
    Object.values(LogLevel).forEach(level => {
      if (typeof level === 'number') {
        stats.byLevel[level] = 0;
      }
    });

    // 统计日志
    this.logs.forEach(log => {
      stats.byLevel[log.level]++;
      if (log.module) {
        stats.byModule[log.module] = (stats.byModule[log.module] || 0) + 1;
      }
    });

    return stats;
  }

  // 创建模块特定的logger
  createModuleLogger(moduleName: string) {
    return {
      debug: (message: string, data?: any) => this.debug(message, data, moduleName),
      info: (message: string, data?: any) => this.info(message, data, moduleName),
      warn: (message: string, data?: any) => this.warn(message, data, moduleName),
      error: (message: string, error?: Error | any) => this.error(message, error, moduleName),
      performance: (operation: string, duration: number, data?: any) => {
        this.performance(`${moduleName}:${operation}`, duration, data);
      }
    };
  }
}

// 创建默认logger实例
export const logger = new Logger();

// 创建常用的模块loggers
export const apiLogger = logger.createModuleLogger('API');
export const wsLogger = logger.createModuleLogger('WebSocket');
export const uiLogger = logger.createModuleLogger('UI');
export const perfLogger = logger.createModuleLogger('Performance');
export const userLogger = logger.createModuleLogger('UserAction');

export default logger;
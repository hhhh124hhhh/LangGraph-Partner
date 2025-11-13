/**
 * React 错误边界组件
 * 捕获和处理React组件树中的错误
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw, Home, MessageCircle } from 'lucide-react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
  errorId: string;
  retryCount: number;
}

export class ErrorBoundary extends Component<Props, State> {
  private maxRetries = 3;

  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: '',
      retryCount: 0
    };
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return {
      hasError: true,
      error,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('[ErrorBoundary] 捕获到错误:', error, errorInfo);

    this.setState({
      error,
      errorInfo
    });

    // 记录错误信息
    this.logError(error, errorInfo);

    // 调用外部错误处理函数
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // 发送错误报告（可选）
    this.reportError(error, errorInfo);
  }

  private logError(error: Error, errorInfo: ErrorInfo): void {
    const errorData = {
      message: error.message,
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      errorId: this.state.errorId
    };

    // 在开发环境输出详细错误信息
    if (process.env.NODE_ENV === 'development') {
      console.group(`🚨 Error ${this.state.errorId}`);
      console.error('Error:', error);
      console.error('Error Info:', errorInfo);
      console.error('Full Error Data:', errorData);
      console.groupEnd();
    }

    // 存储到localStorage用于调试
    try {
      const errors = JSON.parse(localStorage.getItem('error_logs') || '[]');
      errors.push(errorData);
      // 只保留最近20个错误
      if (errors.length > 20) {
        errors.shift();
      }
      localStorage.setItem('error_logs', JSON.stringify(errors));
    } catch (e) {
      console.warn('[ErrorBoundary] 无法存储错误日志:', e);
    }
  }

  private reportError = async (error: Error, errorInfo: ErrorInfo): Promise<void> => {
    // 这里可以集成错误报告服务，如Sentry、LogRocket等
    // 目前只在开发环境输出
    if (process.env.NODE_ENV === 'development') {
      console.log('[ErrorBoundary] 错误报告已准备，可以发送到监控服务');
    }
  };

  private handleRetry = (): void => {
    if (this.state.retryCount < this.maxRetries) {
      this.setState(prevState => ({
        hasError: false,
        error: null,
        errorInfo: null,
        retryCount: prevState.retryCount + 1
      }));
    }
  };

  private handleGoHome = (): void => {
    window.location.href = '/';
  };

  private handleReload = (): void => {
    window.location.reload();
  };

  private handleSendFeedback = (): void => {
    const errorDetails = `
错误ID: ${this.state.errorId}
错误信息: ${this.state.error?.message}
组件堆栈: ${this.state.errorInfo?.componentStack}
时间: ${new Date().toLocaleString()}
页面: ${window.location.href}
重试次数: ${this.state.retryCount}
    `;

    // 可以打开邮件客户端或跳转到反馈页面
    window.open(`mailto:support@example.com?subject=错误反馈 - ${this.state.errorId}&body=${encodeURIComponent(errorDetails)}`);
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // 如果提供了自定义fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认错误UI
      return (
        <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
          <div className="max-w-md w-full bg-slate-800 rounded-lg shadow-xl border border-slate-700 p-6">
            <div className="flex items-center justify-center w-16 h-16 bg-red-500/20 rounded-full mb-4 mx-auto">
              <AlertTriangle className="w-8 h-8 text-red-500" />
            </div>

            <h1 className="text-2xl font-bold text-white text-center mb-2">
              哎呀，出错了
            </h1>

            <p className="text-slate-400 text-center mb-6">
              应用程序遇到了意外错误。我们已经记录了这个问题，您可以尝试以下解决方案。
            </p>

            {/* 开发环境显示详细错误信息 */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-6 bg-slate-900 rounded p-4">
                <summary className="text-sm font-medium text-slate-300 cursor-pointer mb-2">
                  错误详情 (开发模式)
                </summary>
                <div className="text-xs text-slate-400 font-mono">
                  <div className="mb-2">
                    <strong>错误ID:</strong> {this.state.errorId}
                  </div>
                  <div className="mb-2">
                    <strong>错误:</strong> {this.state.error.message}
                  </div>
                  <div className="mb-2">
                    <strong>重试次数:</strong> {this.state.retryCount}/{this.maxRetries}
                  </div>
                  {this.state.error.stack && (
                    <details className="mt-2">
                      <summary className="cursor-pointer text-blue-400">堆栈跟踪</summary>
                      <pre className="mt-1 whitespace-pre-wrap">
                        {this.state.error.stack}
                      </pre>
                    </details>
                  )}
                </div>
              </details>
            )}

            {/* 操作按钮 */}
            <div className="space-y-3">
              {this.state.retryCount < this.maxRetries && (
                <button
                  onClick={this.handleRetry}
                  className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  重试 ({this.maxRetries - this.state.retryCount} 次剩余)
                </button>
              )}

              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={this.handleReload}
                  className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 px-4 rounded transition-colors"
                >
                  <RefreshCw className="w-4 h-4" />
                  刷新页面
                </button>

                <button
                  onClick={this.handleGoHome}
                  className="flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-white font-medium py-2 px-4 rounded transition-colors"
                >
                  <Home className="w-4 h-4" />
                  返回首页
                </button>
              </div>

              <button
                onClick={this.handleSendFeedback}
                className="w-full flex items-center justify-center gap-2 border border-slate-600 hover:bg-slate-700 text-slate-300 font-medium py-2 px-4 rounded transition-colors"
              >
                <MessageCircle className="w-4 h-4" />
                发送错误反馈
              </button>
            </div>

            {/* 帮助信息 */}
            <div className="mt-6 p-4 bg-slate-900/50 rounded border border-slate-700">
              <h3 className="text-sm font-medium text-slate-300 mb-2">
                如果问题持续存在：
              </h3>
              <ul className="text-xs text-slate-400 space-y-1">
                <li>• 清除浏览器缓存后重试</li>
                <li>• 检查网络连接是否正常</li>
                <li>• 尝试使用无痕模式</li>
                <li>• 联系技术支持并提供错误ID: {this.state.errorId}</li>
              </ul>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

// 高阶组件版本
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  fallback?: ReactNode,
  onError?: (error: Error, errorInfo: ErrorInfo) => void
) {
  return function WrappedComponent(props: P) {
    return (
      <ErrorBoundary fallback={fallback} onError={onError}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}

// 用于特定错误的简单错误边界
export function SimpleErrorBoundary({
  children,
  message = "内容加载失败",
  onRetry
}: {
  children: ReactNode;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <ErrorBoundary
      fallback={
        <div className="flex flex-col items-center justify-center p-8 text-center">
          <AlertTriangle className="w-12 h-12 text-yellow-500 mb-4" />
          <p className="text-slate-400 mb-4">{message}</p>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded transition-colors"
            >
              重试
            </button>
          )}
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  );
}

export default ErrorBoundary;
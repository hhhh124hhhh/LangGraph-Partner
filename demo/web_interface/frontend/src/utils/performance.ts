/**
 * 性能监控工具
 * 监控LCP、FID、CLS等关键性能指标
 */

export interface PerformanceMetrics {
  lcp: number;
  fid: number;
  cls: number;
  fcp: number;
  ttfb: number;
  domLoad: number;
  windowLoad: number;
}

export interface PerformanceEntry {
  name: string;
  value: number;
  timestamp: number;
}

class PerformanceMonitor {
  private metrics: Partial<PerformanceMetrics> = {};
  private observers: PerformanceObserver[] = [];
  private isSupported = true;

  constructor() {
    this.checkSupport();
    if (this.isSupported) {
      this.initializeObservers();
    }
  }

  private checkSupport(): void {
    this.isSupported = 'PerformanceObserver' in window &&
                     'performance' in window &&
                     'PerformanceNavigationTiming' in window;
  }

  private initializeObservers(): void {
    try {
      // 监控LCP (Largest Contentful Paint)
      this.observeLCP();

      // 监控FID (First Input Delay)
      this.observeFID();

      // 监控CLS (Cumulative Layout Shift)
      this.observeCLS();

      // 监控FCP (First Contentful Paint)
      this.observeFCP();

      // 监控TTI (Time to Interactive) - 通过Long Tasks估算
      this.observeLongTasks();

      // 监控资源加载性能
      this.observeResources();

    } catch (error) {
      console.warn('[Performance] Observer initialization failed:', error);
    }
  }

  private observeLCP(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1] as any;
        if (lastEntry) {
          this.metrics.lcp = Math.round(lastEntry.startTime);
          console.log(`[Performance] LCP: ${this.metrics.lcp}ms`);
          this.reportMetric('LCP', this.metrics.lcp);
        }
      });

      observer.observe({ type: 'largest-contentful-paint', buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn('[Performance] LCP observer failed:', error);
      // 回退方案：通过Navigation Timing计算
      this.calculateLCPFallback();
    }
  }

  private observeFID(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (entry.name === 'first-input') {
            this.metrics.fid = Math.round(entry.processingStart - entry.startTime);
            console.log(`[Performance] FID: ${this.metrics.fid}ms`);
            this.reportMetric('FID', this.metrics.fid);
          }
        });
      });

      observer.observe({ type: 'first-input', buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn('[Performance] FID observer failed:', error);
    }
  }

  private observeCLS(): void {
    try {
      let clsValue = 0;

      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (!entry.hadRecentInput) {
            clsValue += entry.value;
          }
        });

        this.metrics.cls = Math.round(clsValue * 1000) / 1000;
        console.log(`[Performance] CLS: ${this.metrics.cls}`);
        this.reportMetric('CLS', this.metrics.cls);
      });

      observer.observe({ type: 'layout-shift', buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn('[Performance] CLS observer failed:', error);
    }
  }

  private observeFCP(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
        if (fcpEntry) {
          this.metrics.fcp = Math.round(fcpEntry.startTime);
          console.log(`[Performance] FCP: ${this.metrics.fcp}ms`);
          this.reportMetric('FCP', this.metrics.fcp);
        }
      });

      observer.observe({ type: 'paint', buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn('[Performance] FCP observer failed:', error);
    }
  }

  private observeLongTasks(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          console.log(`[Performance] Long Task: ${Math.round(entry.duration)}ms`);
          this.reportMetric('LongTask', entry.duration);
        });
      });

      observer.observe({ type: 'longtask', buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn('[Performance] Long Task observer failed:', error);
    }
  }

  private observeResources(): void {
    try {
      const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry: any) => {
          if (entry.duration > 1000) { // 只记录超过1秒的资源
            console.log(`[Performance] Slow Resource: ${entry.name} - ${Math.round(entry.duration)}ms`);
            this.reportMetric('SlowResource', entry.duration, entry.name);
          }
        });
      });

      observer.observe({ type: 'resource', buffered: true });
      this.observers.push(observer);
    } catch (error) {
      console.warn('[Performance] Resource observer failed:', error);
    }
  }

  private calculateLCPFallback(): void {
    // 回退方案：通过Navigation Timing API估算
    window.addEventListener('load', () => {
      setTimeout(() => {
        const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        if (navigation) {
          this.metrics.lcp = Math.round(navigation.loadEventEnd - navigation.fetchStart);
          console.log(`[Performance] LCP (fallback): ${this.metrics.lcp}ms`);
          this.reportMetric('LCP_fallback', this.metrics.lcp);
        }
      }, 0);
    });
  }

  private reportMetric(name: string, value: number, additionalInfo?: string): void {
    // 这里可以发送到分析服务
    const metric: PerformanceEntry = {
      name,
      value,
      timestamp: Date.now()
    };

    // 发送到控制台（开发环境）
    if (process.env.NODE_ENV === 'development') {
      const info = additionalInfo ? ` (${additionalInfo})` : '';
      console.log(`[Performance] ${name}: ${value}ms${info}`);
    }

    // 可以在这里集成分析服务
    // this.sendToAnalytics(metric);
  }

  // 获取当前性能指标
  getMetrics(): Partial<PerformanceMetrics> {
    // 补充基础指标
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    if (navigation) {
      this.metrics.ttfb = Math.round(navigation.responseStart - navigation.requestStart);
      // 使用更兼容的方式计算，避免navigationStart属性不存在的错误
      const startTime = navigation.startTime;
      this.metrics.domLoad = Math.round((navigation.domContentLoadedEventEnd || 0) - startTime);
      this.metrics.windowLoad = Math.round((navigation.loadEventEnd || 0) - startTime);
    }

    return { ...this.metrics };
  }

  // 获取性能评分
  getPerformanceScore(): number {
    const metrics = this.getMetrics();
    let score = 100;

    // LCP评分 (目标: <2.5s)
    if (metrics.lcp) {
      if (metrics.lcp > 4000) score -= 30;
      else if (metrics.lcp > 2500) score -= 15;
    }

    // FID评分 (目标: <100ms)
    if (metrics.fid) {
      if (metrics.fid > 300) score -= 30;
      else if (metrics.fid > 100) score -= 15;
    }

    // CLS评分 (目标: <0.1)
    if (metrics.cls) {
      if (metrics.cls > 0.25) score -= 30;
      else if (metrics.cls > 0.1) score -= 15;
    }

    // FCP评分 (目标: <1.8s)
    if (metrics.fcp) {
      if (metrics.fcp > 3000) score -= 20;
      else if (metrics.fcp > 1800) score -= 10;
    }

    return Math.max(0, score);
  }

  // 生成性能报告
  generateReport(): string {
    const metrics = this.getMetrics();
    const score = this.getPerformanceScore();

    return `
📊 性能报告 (评分: ${score}/100)

⏱️  加载性能:
   LCP (最大内容绘制): ${metrics.lcp || 'N/A'}ms
   FCP (首次内容绘制): ${metrics.fcp || 'N/A'}ms
   TTFB (首字节时间): ${metrics.ttfb || 'N/A'}ms
   DOM加载时间: ${metrics.domLoad || 'N/A'}ms
   页面加载时间: ${metrics.windowLoad || 'N/A'}ms

🎯 交互性能:
   FID (首次输入延迟): ${metrics.fid || 'N/A'}ms
   CLS (累积布局偏移): ${metrics.cls || 'N/A'}

💡 优化建议:
   ${this.getOptimizationSuggestions()}
    `;
  }

  private getOptimizationSuggestions(): string {
    const metrics = this.getMetrics();
    const suggestions: string[] = [];

    if (metrics.lcp && metrics.lcp > 2500) {
      suggestions.push('• 优化LCP: 压缩图片、使用CDN、优化关键渲染路径');
    }
    if (metrics.fid && metrics.fid > 100) {
      suggestions.push('• 优化FID: 减少主线程阻塞、优化JavaScript执行');
    }
    if (metrics.cls && metrics.cls > 0.1) {
      suggestions.push('• 优化CLS: 为图片设置尺寸、避免动态内容插入');
    }
    if (metrics.ttfb && metrics.ttfb > 600) {
      suggestions.push('• 优化TTFB: 使用CDN、启用服务器缓存、优化API响应');
    }

    return suggestions.length > 0 ? suggestions.join('\n   ') : '• 性能表现良好！继续保持。';
  }

  // 监控特定操作的性能
  measureOperation(name: string, operation: () => void | Promise<void>): Promise<number> {
    const startTime = performance.now();

    const result = operation();

    if (result instanceof Promise) {
      return result.then(() => {
        const duration = performance.now() - startTime;
        console.log(`[Performance] ${name}: ${Math.round(duration)}ms`);
        this.reportMetric(name, duration);
        return duration;
      });
    } else {
      const duration = performance.now() - startTime;
      console.log(`[Performance] ${name}: ${Math.round(duration)}ms`);
      this.reportMetric(name, duration);
      return Promise.resolve(duration);
    }
  }

  // 清理观察器
  destroy(): void {
    this.observers.forEach(observer => {
      observer.disconnect();
    });
    this.observers = [];
  }
}

// 创建单例实例
export const performanceMonitor = new PerformanceMonitor();
export default performanceMonitor;
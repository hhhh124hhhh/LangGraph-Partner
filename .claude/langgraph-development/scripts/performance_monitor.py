#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph性能监控工具

基于Context7调研的企业级性能监控系统，提供实时性能监控、
资源使用分析、性能瓶颈识别和优化建议。
"""

import asyncio
import time
import json
import sys
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
import argparse

try:
    import prometheus_client as prometheus
    from prometheus_client import Counter, Histogram, Gauge, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("[WARNING] Prometheus客户端不可用，将使用内置监控")

try:
    from langgraph.graph import StateGraph
    from langgraph.checkpoint.memory import MemorySaver
except ImportError:
    print("[ERROR] 缺少LangGraph依赖")
    sys.exit(1)


@dataclass
class PerformanceMetrics:
    """性能指标数据类"""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_mb: float
    execution_time: float
    nodes_executed: int
    tools_called: int
    errors_count: int
    throughput: float
    response_time_p95: float
    response_time_p99: float


class PerformanceMonitor:
    """LangGraph性能监控器"""

    def __init__(self, enable_prometheus: bool = False, prometheus_port: int = 8000):
        self.metrics_history: List[PerformanceMetrics] = []
        self.monitoring = False
        self.callbacks: List[Callable] = []

        # 性能统计
        self.execution_times: List[float] = []
        self.node_execution_counts: Dict[str, int] = {}
        self.tool_call_counts: Dict[str, int] = {}
        self.error_counts: Dict[str, int] = {}

        # Prometheus指标
        self.enable_prometheus = enable_prometheus and PROMETHEUS_AVAILABLE
        if self.enable_prometheus:
            self._setup_prometheus_metrics(prometheus_port)

    def _setup_prometheus_metrics(self, port: int):
        """设置Prometheus指标"""
        try:
            # 执行时间直方图
            self.execution_time_histogram = Histogram(
                'langgraph_execution_time_seconds',
                'LangGraph执行时间',
                ['node_name']
            )

            # 请求计数器
            self.request_counter = Counter(
                'langgraph_requests_total',
                'LangGraph请求总数',
                ['status', 'node_name']
            )

            # 工具调用计数器
            self.tool_call_counter = Counter(
                'langgraph_tool_calls_total',
                '工具调用总数',
                ['tool_name']
            )

            # 资源使用量规
            self.cpu_usage_gauge = Gauge('langgraph_cpu_usage_percent', 'CPU使用率')
            self.memory_usage_gauge = Gauge('langgraph_memory_usage_percent', '内存使用率')

            # 启动HTTP服务器
            start_http_server(port)
            print(f"[INFO] Prometheus监控服务启动在端口 {port}")
        except Exception as e:
            print(f"[WARNING] Prometheus指标设置失败: {e}")
            self.enable_prometheus = False

    def add_callback(self, callback: Callable[[PerformanceMetrics], None]):
        """添加性能监控回调函数"""
        self.callbacks.append(callback)

    def start_monitoring(self, interval: float = 1.0):
        """启动性能监控"""
        if self.monitoring:
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        print(f"[INFO] 性能监控已启动，采样间隔: {interval}秒")

    def stop_monitoring(self):
        """停止性能监控"""
        self.monitoring = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        print("[INFO] 性能监控已停止")

    def _monitor_loop(self, interval: float):
        """监控循环"""
        while self.monitoring:
            try:
                # 收集系统指标
                cpu_percent = psutil.cpu_percent()
                memory_info = psutil.virtual_memory()

                # 计算性能指标
                metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    cpu_usage=cpu_percent,
                    memory_usage=memory_info.percent,
                    memory_mb=memory_info.used / 1024 / 1024,
                    execution_time=0.0,
                    nodes_executed=sum(self.node_execution_counts.values()),
                    tools_called=sum(self.tool_call_counts.values()),
                    errors_count=sum(self.error_counts.values()),
                    throughput=self._calculate_throughput(),
                    response_time_p95=self._calculate_percentile(95),
                    response_time_p99=self._calculate_percentile(99)
                )

                # 更新Prometheus指标
                if self.enable_prometheus:
                    self.cpu_usage_gauge.set(cpu_percent)
                    self.memory_usage_gauge.set(memory_info.percent)

                # 存储指标历史
                self.metrics_history.append(metrics)

                # 限制历史数据量（保留最近1小时）
                cutoff_time = datetime.now() - timedelta(hours=1)
                self.metrics_history = [
                    m for m in self.metrics_history
                    if m.timestamp > cutoff_time
                ]

                # 调用回调函数
                for callback in self.callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        print(f"[WARNING] 回调函数执行失败: {e}")

            except Exception as e:
                print(f"[ERROR] 监控数据收集失败: {e}")

            time.sleep(interval)

    def _calculate_throughput(self) -> float:
        """计算吞吐量（每秒执行的节点数）"""
        if not self.metrics_history:
            return 0.0

        # 计算最近1分钟的吞吐量
        cutoff_time = datetime.now() - timedelta(minutes=1)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        if len(recent_metrics) < 2:
            return 0.0

        total_nodes = recent_metrics[-1].nodes_executed - recent_metrics[0].nodes_executed
        time_span = (recent_metrics[-1].timestamp - recent_metrics[0].timestamp).total_seconds()

        return total_nodes / time_span if time_span > 0 else 0.0

    def _calculate_percentile(self, percentile: float) -> float:
        """计算响应时间百分位数"""
        if not self.execution_times:
            return 0.0

        sorted_times = sorted(self.execution_times)
        index = int(len(sorted_times) * percentile / 100)
        return sorted_times[min(index, len(sorted_times) - 1)]

    def record_execution_start(self, node_name: str) -> str:
        """记录节点执行开始"""
        execution_id = f"{node_name}_{int(time.time() * 1000000)}"
        self._execution_starts[execution_id] = {
            'node_name': node_name,
            'start_time': time.time()
        }
        return execution_id

    def record_execution_end(self, execution_id: str, success: bool = True):
        """记录节点执行结束"""
        if execution_id not in self._execution_starts:
            return

        start_info = self._execution_starts.pop(execution_id)
        execution_time = time.time() - start_info['start_time']
        node_name = start_info['node_name']

        # 记录执行时间
        self.execution_times.append(execution_time)
        self.node_execution_counts[node_name] = \
            self.node_execution_counts.get(node_name, 0) + 1

        # 更新Prometheus指标
        if self.enable_prometheus:
            self.execution_time_histogram.labels(node_name=node_name).observe(execution_time)
            status = "success" if success else "error"
            self.request_counter.labels(status=status, node_name=node_name).inc()

        if not success:
            self.error_counts[node_name] = self.error_counts.get(node_name, 0) + 1

    def record_tool_call(self, tool_name: str):
        """记录工具调用"""
        self.tool_call_counts[tool_name] = self.tool_call_counts.get(tool_name, 0) + 1

        if self.enable_prometheus:
            self.tool_call_counter.labels(tool_name=tool_name).inc()

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """获取当前性能指标"""
        return self.metrics_history[-1] if self.metrics_history else None

    def generate_performance_report(self, duration_minutes: int = 10) -> str:
        """生成性能报告"""
        cutoff_time = datetime.now() - timedelta(minutes=duration_minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp > cutoff_time
        ]

        if not recent_metrics:
            return "没有可用的性能数据"

        # 计算统计数据
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_throughput = sum(m.throughput for m in recent_metrics) / len(recent_metrics)
        max_memory_mb = max(m.memory_mb for m in recent_metrics)

        # 错误率
        total_executions = sum(self.node_execution_counts.values())
        total_errors = sum(self.error_counts.values())
        error_rate = (total_errors / total_executions * 100) if total_executions > 0 else 0

        report = f"""
# LangGraph性能监控报告

## 时间范围
- **报告期间**: 最近 {duration_minutes} 分钟
- **数据点数量**: {len(recent_metrics)}

## 系统资源使用
- **平均CPU使用率**: {avg_cpu:.1f}%
- **平均内存使用率**: {avg_memory:.1f}%
- **峰值内存使用**: {max_memory_mb:.1f} MB

## 执行性能
- **平均吞吐量**: {avg_throughput:.2f} 节点/秒
- **P95响应时间**: {self._calculate_percentile(95):.3f} 秒
- **P99响应时间**: {self._calculate_percentile(99):.3f} 秒
- **错误率**: {error_rate:.2f}%

## 节点执行统计
{self._format_execution_stats()}

## 工具调用统计
{self._format_tool_stats()}

## 性能建议
{self._generate_performance_recommendations(avg_cpu, avg_memory, error_rate)}

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        return report.strip()

    def _format_execution_stats(self) -> str:
        """格式化执行统计"""
        if not self.node_execution_counts:
            return "- 没有节点执行数据"

        stats = []
        total = sum(self.node_execution_counts.values())
        for node_name, count in sorted(self.node_execution_counts.items(),
                                      key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            error_count = self.error_counts.get(node_name, 0)
            stats.append(f"- {node_name}: {count} 次 ({percentage:.1f}%, 错误: {error_count})")

        return "\n".join(stats[:10])  # 只显示前10个

    def _format_tool_stats(self) -> str:
        """格式化工具统计"""
        if not self.tool_call_counts:
            return "- 没有工具调用数据"

        stats = []
        total = sum(self.tool_call_counts.values())
        for tool_name, count in sorted(self.tool_call_counts.items(),
                                     key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            stats.append(f"- {tool_name}: {count} 次 ({percentage:.1f}%)")

        return "\n".join(stats[:10])  # 只显示前10个

    def _generate_performance_recommendations(self, avg_cpu: float,
                                            avg_memory: float, error_rate: float) -> str:
        """生成性能优化建议"""
        recommendations = []

        if avg_cpu > 80:
            recommendations.append("- CPU使用率较高，考虑优化算法或增加并行处理")
        elif avg_cpu > 60:
            recommendations.append("- CPU使用率中等，监控是否有进一步优化空间")

        if avg_memory > 85:
            recommendations.append("- 内存使用率过高，考虑优化内存使用或增加内存")
        elif avg_memory > 70:
            recommendations.append("- 内存使用率较高，注意内存泄漏风险")

        if error_rate > 5:
            recommendations.append("- 错误率较高，建议增加错误处理和重试机制")
        elif error_rate > 1:
            recommendations.append("- 检查错误原因，优化异常处理")

        if not recommendations:
            recommendations.append("- 当前性能表现良好")

        return "\n".join(recommendations)

    def save_metrics_history(self, output_path: str):
        """保存指标历史到文件"""
        output_file = Path(output_path)

        # 转换为JSON可序列化格式
        serializable_data = {
            "metrics_history": [
                {
                    **asdict(metric),
                    "timestamp": metric.timestamp.isoformat()
                }
                for metric in self.metrics_history
            ],
            "execution_times": self.execution_times,
            "node_execution_counts": self.node_execution_counts,
            "tool_call_counts": self.tool_call_counts,
            "error_counts": self.error_counts
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] 性能数据已保存到: {output_file}")


def create_monitoring_wrapper(graph: StateGraph, monitor: PerformanceMonitor):
    """创建性能监控包装器"""

    def monitored_node(node_func):
        """节点监控包装器"""
        def wrapper(state):
            node_name = node_func.__name__
            execution_id = monitor.record_execution_start(node_name)

            try:
                result = node_func(state)
                monitor.record_execution_end(execution_id, success=True)
                return result
            except Exception as e:
                monitor.record_execution_end(execution_id, success=False)
                raise

        wrapper.__name__ = f"monitored_{node_func.__name__}"
        return wrapper

    # 包装所有节点
    for node_name, node_func in graph.nodes.items():
        graph.nodes[node_name] = monitored_node(node_func)

    return graph


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangGraph性能监控工具")
    parser.add_argument("--duration", type=int, default=60,
                       help="监控持续时间（秒）")
    parser.add_argument("--interval", type=float, default=1.0,
                       help="采样间隔（秒）")
    parser.add_argument("--prometheus", action="store_true",
                       help="启用Prometheus监控")
    parser.add_argument("--prometheus-port", type=int, default=8000,
                       help="Prometheus端口")
    parser.add_argument("--output", default="./performance_data.json",
                       help="性能数据输出文件")
    parser.add_argument("--report-duration", type=int, default=10,
                       help="报告时间范围（分钟）")

    args = parser.parse_args()

    print("=" * 60)
    print("LangGraph性能监控工具")
    print("=" * 60)
    print(f"监控持续时间: {args.duration} 秒")
    print(f"采样间隔: {args.interval} 秒")
    print(f"Prometheus: {args.prometheus}")
    if args.prometheus:
        print(f"Prometheus端口: {args.prometheus_port}")
    print()

    # 创建性能监控器
    monitor = PerformanceMonitor(
        enable_prometheus=args.prometheus,
        prometheus_port=args.prometheus_port
    )

    # 启动监控
    monitor.start_monitoring(args.interval)

    try:
        print(f"[INFO] 监控运行中，按 Ctrl+C 停止...")
        await asyncio.sleep(args.duration)
    except KeyboardInterrupt:
        print("\n[INFO] 收到中断信号，正在停止监控...")
    finally:
        monitor.stop_monitoring()

    # 生成性能报告
    print("\n" + "=" * 60)
    print("性能监控报告")
    print("=" * 60)
    report = monitor.generate_performance_report(args.report_duration)
    print(report)

    # 保存数据
    if args.output:
        monitor.save_metrics_history(args.output)

    print("[INFO] 性能监控完成")


if __name__ == "__main__":
    # 初始化执行开始时间字典
    if not hasattr(main, '_execution_starts'):
        main._execution_starts = {}

    asyncio.run(main())
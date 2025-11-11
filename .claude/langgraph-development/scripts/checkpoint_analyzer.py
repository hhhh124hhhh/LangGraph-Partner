#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph检查点分析工具

基于Context7调研的企业级状态管理分析工具，用于分析LangGraph检查点数据、
状态历史和执行模式，帮助开发者优化工作流性能和调试问题。
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import argparse

try:
    from langgraph.checkpoint.memory import MemorySaver
    from langgraph.checkpoint.postgres import PostgresSaver
    from langgraph_checkpoint_redis import RedisSaver
except ImportError as e:
    print(f"[ERROR] 缺少必要的LangGraph依赖: {e}")
    print("请运行: pip install langgraph langgraph-checkpoint-postgres langgraph-checkpoint-redis")
    sys.exit(1)


class CheckpointAnalyzer:
    """LangGraph检查点分析器"""

    def __init__(self, checkpointer, config: Dict[str, Any] = None):
        self.checkpointer = checkpointer
        self.config = config or {}
        self.analysis_results = {}

    async def analyze_thread_history(self, thread_id: str) -> Dict[str, Any]:
        """分析特定线程的完整历史"""
        print(f"[INFO] 分析线程 {thread_id} 的历史...")

        try:
            # 获取检查点历史
            checkpoints = []
            async for checkpoint in self.checkpointer.alist(thread_id):
                checkpoints.append(checkpoint)

            if not checkpoints:
                return {"error": f"线程 {thread_id} 没有检查点数据"}

            # 分析统计数据
            analysis = {
                "thread_id": thread_id,
                "total_checkpoints": len(checkpoints),
                "time_span": self._calculate_time_span(checkpoints),
                "execution_pattern": self._analyze_execution_pattern(checkpoints),
                "state_evolution": self._analyze_state_evolution(checkpoints),
                "performance_metrics": self._calculate_performance_metrics(checkpoints),
                "error_patterns": self._identify_error_patterns(checkpoints),
                "checkpoints": checkpoints
            }

            return analysis

        except Exception as e:
            return {"error": f"分析失败: {str(e)}"}

    def _calculate_time_span(self, checkpoints: List) -> Dict[str, Any]:
        """计算时间跨度"""
        if len(checkpoints) < 2:
            return {"duration_seconds": 0, "start_time": None, "end_time": None}

        start_time = checkpoints[0].metadata.get("ts")
        end_time = checkpoints[-1].metadata.get("ts")

        if start_time and end_time:
            duration = (end_time - start_time).total_seconds()
            return {
                "duration_seconds": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_formatted": str(timedelta(seconds=int(duration)))
            }

        return {"duration_seconds": 0, "start_time": None, "end_time": None}

    def _analyze_execution_pattern(self, checkpoints: List) -> Dict[str, Any]:
        """分析执行模式"""
        pattern = {
            "node_sequence": [],
            "execution_frequency": {},
            "branch_points": [],
            "loop_patterns": []
        }

        for checkpoint in checkpoints:
            # 提取节点执行信息
            metadata = checkpoint.metadata
            if "source" in metadata:
                pattern["node_sequence"].append(metadata["source"])
                pattern["execution_frequency"][metadata["source"]] = \
                    pattern["execution_frequency"].get(metadata["source"], 0) + 1

            # 识别分支点
            if metadata.get("step") and metadata.get("step") > 1:
                pattern["branch_points"].append(metadata["step"])

        # 识别循环模式
        pattern["loop_patterns"] = self._detect_loops(pattern["node_sequence"])

        return pattern

    def _detect_loops(self, node_sequence: List[str]) -> List[Dict[str, Any]]:
        """检测循环模式"""
        loops = []
        sequence_str = " -> ".join(node_sequence)

        # 简单的循环检测
        for i in range(len(node_sequence)):
            for j in range(i + 1, len(node_sequence)):
                if node_sequence[i] == node_sequence[j]:
                    # 找到潜在循环
                    loop_length = j - i
                    if loop_length > 1:  # 排除相邻重复
                        loops.append({
                            "start_index": i,
                            "end_index": j,
                            "loop_length": loop_length,
                            "pattern": " -> ".join(node_sequence[i:j+1])
                        })

        return loops

    def _analyze_state_evolution(self, checkpoints: List) -> Dict[str, Any]:
        """分析状态演化"""
        evolution = {
            "state_size_changes": [],
            "key_transitions": [],
            "message_count_trend": [],
            "error_occurrences": []
        }

        previous_state_size = 0

        for i, checkpoint in enumerate(checkpoints):
            # 计算状态大小变化
            state_size = len(str(checkpoint.channel_values)) if checkpoint.channel_values else 0
            evolution["state_size_changes"].append({
                "checkpoint_index": i,
                "state_size": state_size,
                "change": state_size - previous_state_size
            })
            previous_state_size = state_size

            # 分析消息数量趋势
            if "messages" in checkpoint.channel_values:
                messages = checkpoint.channel_values["messages"]
                evolution["message_count_trend"].append({
                    "checkpoint_index": i,
                    "message_count": len(messages) if messages else 0
                })

            # 检测错误
            if checkpoint.metadata.get("error"):
                evolution["error_occurrences"].append({
                    "checkpoint_index": i,
                    "error": checkpoint.metadata["error"],
                    "timestamp": checkpoint.metadata.get("ts")
                })

        return evolution

    def _calculate_performance_metrics(self, checkpoints: List) -> Dict[str, Any]:
        """计算性能指标"""
        metrics = {
            "total_execution_time": 0,
            "average_step_time": 0,
            "slowest_steps": [],
            "throughput": 0
        }

        if len(checkpoints) < 2:
            return metrics

        step_times = []
        for i in range(1, len(checkpoints)):
            prev_time = checkpoints[i-1].metadata.get("ts")
            curr_time = checkpoints[i].metadata.get("ts")

            if prev_time and curr_time:
                step_time = (curr_time - prev_time).total_seconds()
                step_times.append(step_time)

        if step_times:
            metrics["total_execution_time"] = sum(step_times)
            metrics["average_step_time"] = sum(step_times) / len(step_times)

            # 找出最慢的步骤
            max_time = max(step_times)
            metrics["slowest_steps"] = [
                {
                    "step_index": i + 1,
                    "time_seconds": step_times[i],
                    "time_formatted": str(timedelta(seconds=int(step_times[i])))
                }
                for i, time in enumerate(step_times)
                if time >= max_time * 0.8  # 最慢80%的步骤
            ]

            # 计算吞吐量
            total_time = metrics["total_execution_time"]
            if total_time > 0:
                metrics["throughput"] = len(step_times) / total_time

        return metrics

    def _identify_error_patterns(self, checkpoints: List) -> List[Dict[str, Any]]:
        """识别错误模式"""
        error_patterns = []

        for i, checkpoint in enumerate(checkpoints):
            error = checkpoint.metadata.get("error")
            if error:
                error_patterns.append({
                    "checkpoint_index": i,
                    "error_type": type(error).__name__ if isinstance(error, Exception) else str(type(error)),
                    "error_message": str(error),
                    "node": checkpoint.metadata.get("source"),
                    "timestamp": checkpoint.metadata.get("ts")
                })

        return error_patterns

    async def generate_summary_report(self, thread_id: str) -> str:
        """生成汇总报告"""
        analysis = await self.analyze_thread_history(thread_id)

        if "error" in analysis:
            return f"分析失败: {analysis['error']}"

        report = f"""
# LangGraph 检查点分析报告

## 线程信息
- **线程ID**: {analysis['thread_id']}
- **检查点总数**: {analysis['total_checkpoints']}
- **时间跨度**: {analysis['time_span'].get('duration_formatted', 'N/A')}

## 执行统计
- **平均执行时间**: {analysis['performance_metrics'].get('average_step_time', 0):.2f}秒/步骤
- **总执行时间**: {analysis['performance_metrics'].get('total_execution_time', 0):.2f}秒
- **吞吐量**: {analysis['performance_metrics'].get('throughput', 0):.2f}步骤/秒

## 执行模式分析
- **执行节点序列**: {' -> '.join(analysis['execution_pattern']['node_sequence'])}
- **节点执行频率**: {analysis['execution_pattern']['execution_frequency']}
- **检测到的循环**: {len(analysis['execution_pattern']['loop_patterns'])}

## 错误分析
- **错误总数**: {len(analysis['error_patterns'])}
{chr(10).join([f"- {err['error_type']}: {err['error_message']}" for err in analysis['error_patterns'][:5]])}

## 性能建议
{self._generate_performance_suggestions(analysis)}

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        return report.strip()

    def _generate_performance_suggestions(self, analysis: Dict[str, Any]) -> str:
        """生成性能优化建议"""
        suggestions = []

        # 基于执行时间的建议
        avg_time = analysis['performance_metrics'].get('average_step_time', 0)
        if avg_time > 5.0:
            suggestions.append("- 平均步骤执行时间较长，考虑优化节点逻辑或使用并行执行")

        # 基于循环模式的建议
        loops = analysis['execution_pattern']['loop_patterns']
        if len(loops) > 0:
            suggestions.append(f"- 检测到 {len(loops)} 个循环模式，确认是否为预期行为")

        # 基于错误模式的建议
        if len(analysis['error_patterns']) > 0:
            suggestions.append("- 发现执行错误，建议增加错误处理和重试机制")

        # 基于状态演化的建议
        state_changes = analysis['state_evolution']['state_size_changes']
        if state_changes:
            max_change = max(abs(change['change']) for change in state_changes)
            if max_change > 1000:
                suggestions.append("- 状态大小变化较大，考虑优化状态管理策略")

        return "\n".join(suggestions) if suggestions else "- 当前执行性能良好，无明显优化点"

    async def save_analysis(self, thread_id: str, output_path: str):
        """保存分析结果到文件"""
        analysis = await self.analyze_thread_history(thread_id)
        report = await self.generate_summary_report(thread_id)

        # 保存详细分析数据
        analysis_path = Path(output_path) / f"{thread_id}_analysis.json"
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str, ensure_ascii=False)

        # 保存报告
        report_path = Path(output_path) / f"{thread_id}_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"[SUCCESS] 分析结果已保存:")
        print(f"  - 详细数据: {analysis_path}")
        print(f"  - 分析报告: {report_path}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangGraph检查点分析工具")
    parser.add_argument("--checkpointer", choices=["memory", "postgres", "redis"],
                       default="memory", help="检查点类型")
    parser.add_argument("--thread-id", required=True, help="要分析的线程ID")
    parser.add_argument("--connection-string", help="数据库连接字符串")
    parser.add_argument("--output", default="./analysis_output", help="输出目录")
    parser.add_argument("--report", action="store_true", help="生成汇总报告")
    parser.add_argument("--list-threads", action="store_true", help="列出所有线程")

    args = parser.parse_args()

    # 初始化检查点存储器
    try:
        if args.checkpointer == "memory":
            checkpointer = MemorySaver()
        elif args.checkpointer == "postgres":
            if not args.connection_string:
                print("[ERROR] PostgreSQL需要连接字符串")
                sys.exit(1)
            checkpointer = PostgresSaver.from_conn_string(args.connection_string)
        elif args.checkpointer == "redis":
            if not args.connection_string:
                print("[ERROR] Redis需要连接字符串")
                sys.exit(1)
            checkpointer = RedisSaver.from_conn_string(args.connection_string)
    except Exception as e:
        print(f"[ERROR] 检查点存储器初始化失败: {e}")
        sys.exit(1)

    # 创建分析器
    analyzer = CheckpointAnalyzer(checkpointer)

    # 创建输出目录
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("LangGraph检查点分析工具")
    print("=" * 60)
    print(f"检查点类型: {args.checkpointer}")
    print(f"输出目录: {output_dir}")
    print()

    try:
        if args.list_threads:
            # 列出所有线程
            print("[INFO] 获取线程列表...")
            threads = set()
            async for config in checkpointer.alist():
                if hasattr(config, 'config') and config.config:
                    thread_id = config.config.get('thread_id')
                    if thread_id:
                        threads.add(thread_id)

            if threads:
                print(f"[INFO] 找到 {len(threads)} 个线程:")
                for thread_id in sorted(threads):
                    print(f"  - {thread_id}")
            else:
                print("[INFO] 没有找到线程数据")

        else:
            # 分析指定线程
            print(f"[INFO] 开始分析线程: {args.thread_id}")

            if args.report:
                # 生成并显示报告
                report = await analyzer.generate_summary_report(args.thread_id)
                print("\n" + "=" * 60)
                print("分析报告")
                print("=" * 60)
                print(report)

            # 保存分析结果
            await analyzer.save_analysis(args.thread_id, output_dir)

    except Exception as e:
        print(f"[ERROR] 分析失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
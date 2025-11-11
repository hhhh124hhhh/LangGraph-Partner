#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph代理测试框架

基于Context7调研的企业级测试工具，提供单元测试、集成测试、
性能测试和端到端测试功能。
"""

import asyncio
import json
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
import argparse

try:
    import pytest
    import aiohttp
    from langchain_core.messages import HumanMessage, AIMessage
    from langgraph.graph import StateGraph, MessageGraph
    from langgraph.checkpoint.memory import MemorySaver
    LANGGRAPH_AVAILABLE = True
except ImportError as e:
    print(f"[WARNING] 缺少必要依赖: {e}")
    LANGGRAPH_AVAILABLE = False


@dataclass
class TestCase:
    """测试用例数据类"""
    name: str
    description: str
    input_data: Dict[str, Any]
    expected_output: Optional[Dict[str, Any]] = None
    timeout: float = 30.0
    category: str = "general"


@dataclass
class TestResult:
    """测试结果数据类"""
    test_name: str
    status: str  # "passed", "failed", "timeout", "error"
    duration: float
    output: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    assertion_errors: List[str] = None


class AgentTester:
    """LangGraph代理测试器"""

    def __init__(self, graph_or_agent, config: Dict[str, Any] = None):
        """
        初始化测试器

        Args:
            graph_or_agent: LangGraph图或代理实例
            config: 测试配置
        """
        self.graph_or_agent = graph_or_agent
        self.config = config or {}
        self.test_cases: List[TestCase] = []
        self.test_results: List[TestResult] = []
        self.test_data: Dict[str, Any] = {}

    def add_test_case(self, test_case: TestCase):
        """添加测试用例"""
        self.test_cases.append(test_case)

    def add_test_cases_from_file(self, file_path: str):
        """从文件加载测试用例"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for test_data in data.get('test_cases', []):
                test_case = TestCase(**test_data)
                self.add_test_case(test_case)

            self.test_data = data
            print(f"[INFO] 从 {file_path} 加载了 {len(data.get('test_cases', []))} 个测试用例")

        except Exception as e:
            print(f"[ERROR] 加载测试用例失败: {e}")

    async def run_single_test(self, test_case: TestCase) -> TestResult:
        """运行单个测试用例"""
        start_time = time.time()

        try:
            # 执行测试
            if hasattr(self.graph_or_agent, 'ainvoke'):
                # LangGraph图
                result = await asyncio.wait_for(
                    self.graph_or_agent.ainvoke(
                        test_case.input_data,
                        config=self.config
                    ),
                    timeout=test_case.timeout
                )
            elif hasattr(self.graph_or_agent, '__call__'):
                # 可调用对象
                result = await asyncio.wait_for(
                    self.graph_or_agent(test_case.input_data),
                    timeout=test_case.timeout
                )
            else:
                # 同步调用
                result = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.graph_or_agent,
                        test_case.input_data
                    ),
                    timeout=test_case.timeout
                )

            duration = time.time() - start_time

            # 验证预期输出
            assertion_errors = []
            if test_case.expected_output:
                assertion_errors = self._verify_output(result, test_case.expected_output)

            status = "failed" if assertion_errors else "passed"

            return TestResult(
                test_name=test_case.name,
                status=status,
                duration=duration,
                output=result,
                assertion_errors=assertion_errors
            )

        except asyncio.TimeoutError:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_case.name,
                status="timeout",
                duration=duration,
                error_message=f"测试超时（{test_case.timeout}秒）"
            )

        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                test_name=test_case.name,
                status="error",
                duration=duration,
                error_message=str(e),
                assertion_errors=None
            )

    def _verify_output(self, actual: Any, expected: Dict[str, Any]) -> List[str]:
        """验证输出是否符合预期"""
        errors = []

        try:
            if 'contains' in expected:
                # 检查输出是否包含指定内容
                for item in expected['contains']:
                    if isinstance(item, str):
                        if item.lower() not in str(actual).lower():
                            errors.append(f"输出中未找到预期内容: {item}")
                    else:
                        if item not in str(actual):
                            errors.append(f"输出中未找到预期内容: {item}")

            if 'equals' in expected:
                # 检查输出是否等于预期值
                if actual != expected['equals']:
                    errors.append(f"输出不等于预期值")

            if 'type' in expected:
                # 检查输出类型
                expected_type = expected['type']
                if expected_type == 'str' and not isinstance(actual, str):
                    errors.append(f"输出类型不是字符串: {type(actual)}")
                elif expected_type == 'dict' and not isinstance(actual, dict):
                    errors.append(f"输出类型不是字典: {type(actual)}")
                elif expected_type == 'list' and not isinstance(actual, list):
                    errors.append(f"输出类型不是列表: {type(actual)}")

            if 'min_length' in expected:
                # 检查最小长度
                min_length = expected['min_length']
                if isinstance(actual, (str, list)):
                    if len(actual) < min_length:
                        errors.append(f"输出长度小于最小要求: {len(actual)} < {min_length}")
                elif isinstance(actual, dict):
                    if len(actual) < min_length:
                        errors.append(f"输出项数少于最小要求: {len(actual)} < {min_length}")

            if 'max_length' in expected:
                # 检查最大长度
                max_length = expected['max_length']
                if isinstance(actual, (str, list)):
                    if len(actual) > max_length:
                        errors.append(f"输出长度超过最大限制: {len(actual)} > {max_length}")
                elif isinstance(actual, dict):
                    if len(actual) > max_length:
                        errors.append(f"输出项数超过最大限制: {len(actual)} > {max_length}")

            if 'contains_keys' in expected and isinstance(actual, dict):
                # 检查字典是否包含指定键
                missing_keys = set(expected['contains_keys']) - set(actual.keys())
                if missing_keys:
                    errors.append(f"输出字典缺少键: {missing_keys}")

        except Exception as e:
            errors.append(f"验证过程中出错: {str(e)}")

        return errors

    async def run_all_tests(self) -> List[TestResult]:
        """运行所有测试用例"""
        if not self.test_cases:
            print("[WARNING] 没有测试用例可运行")
            return []

        print(f"[INFO] 开始运行 {len(self.test_cases)} 个测试用例...")
        self.test_results = []

        for i, test_case in enumerate(self.test_cases, 1):
            print(f"[INFO] 运行测试 {i}/{len(self.test_cases)}: {test_case.name}")

            result = await self.run_single_test(test_case)
            self.test_results.append(result)

            # 输出测试结果
            status_symbol = {
                "passed": "✅",
                "failed": "❌",
                "timeout": "⏰",
                "error": "💥"
            }.get(result.status, "❓")

            print(f"[{status_symbol}] {test_case.name}: {result.status} "
                  f"({result.duration:.2f}s)")

            if result.error_message:
                print(f"    错误: {result.error_message}")

            if result.assertion_errors:
                for error in result.assertion_errors:
                    print(f"    断言失败: {error}")

        return self.test_results

    def generate_test_report(self) -> str:
        """生成测试报告"""
        if not self.test_results:
            return "没有测试结果"

        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r.status == "passed")
        failed_tests = sum(1 for r in self.test_results if r.status == "failed")
        timeout_tests = sum(1 for r in self.test_results if r.status == "timeout")
        error_tests = sum(1 for r in self.test_results if r.status == "error")

        total_duration = sum(r.duration for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0

        report = f"""
# LangGraph代理测试报告

## 测试概览
- **总测试数**: {total_tests}
- **通过**: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
- **失败**: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
- **超时**: {timeout_tests} ({timeout_tests/total_tests*100:.1f}%)
- **错误**: {error_tests} ({error_tests/total_tests*100:.1f}%)
- **总耗时**: {total_duration:.2f} 秒
- **平均耗时**: {avg_duration:.2f} 秒

## 详细结果

### 通过的测试
{self._format_test_results([r for r in self.test_results if r.status == "passed"])}

### 失败的测试
{self._format_test_results([r for r in self.test_results if r.status == "failed"])}

### 超时的测试
{self._format_test_results([r for r in self.test_results if r.status == "timeout"])}

### 错误的测试
{self._format_test_results([r for r in self.test_results if r.status == "error"])}

## 性能分析
{self._analyze_performance()}

## 建议和改进
{self._generate_recommendations()}

---
报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """

        return report.strip()

    def _format_test_results(self, results: List[TestResult]) -> str:
        """格式化测试结果列表"""
        if not results:
            return "- 无"

        formatted = []
        for result in results:
            line = f"- **{result.test_name}**: {result.duration:.2f}s"
            if result.error_message:
                line += f" - {result.error_message}"
            if result.assertion_errors:
                for error in result.assertion_errors[:2]:  # 只显示前2个错误
                    line += f"\n  - {error}"
            formatted.append(line)

        return "\n".join(formatted)

    def _analyze_performance(self) -> str:
        """分析测试性能"""
        if not self.test_results:
            return "- 没有性能数据"

        durations = [r.duration for r in self.test_results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)

        slow_tests = [r for r in self.test_results if r.duration > avg_duration * 2]

        analysis = f"""
- **平均执行时间**: {avg_duration:.2f} 秒
- **最快执行时间**: {min_duration:.2f} 秒
- **最慢执行时间**: {max_duration:.2f} 秒
- **慢速测试**: {len(slow_tests)} 个
        """

        if slow_tests:
            analysis += f"\n\n### 慢速测试\n"
            for test in sorted(slow_tests, key=lambda x: x.duration, reverse=True)[:5]:
                analysis += f"- {test.test_name}: {test.duration:.2f}s\n"

        return analysis.strip()

    def _generate_recommendations(self) -> str:
        """生成改进建议"""
        recommendations = []

        failed_count = sum(1 for r in self.test_results if r.status == "failed")
        error_count = sum(1 for r in self.test_results if r.status == "error")
        timeout_count = sum(1 for r in self.test_results if r.status == "timeout")

        if failed_count > 0:
            recommendations.append(f"- 有 {failed_count} 个测试失败，检查预期输出设置")

        if error_count > 0:
            recommendations.append(f"- 有 {error_count} 个测试出现错误，检查代理实现和错误处理")

        if timeout_count > 0:
            recommendations.append(f"- 有 {timeout_count} 个测试超时，考虑增加超时时间或优化性能")

        avg_duration = sum(r.duration for r in self.test_results) / len(self.test_results)
        if avg_duration > 5.0:
            recommendations.append("- 平均测试时间较长，考虑性能优化")

        if not recommendations:
            recommendations.append("- 所有测试表现良好，继续保持代码质量")

        return "\n".join(recommendations)

    def save_test_results(self, output_path: str):
        """保存测试结果"""
        output_file = Path(output_path)

        # 转换为JSON可序列化格式
        serializable_results = []
        for result in self.test_results:
            result_dict = asdict(result)
            if result.output:
                # 简化输出以便JSON序列化
                try:
                    result_dict['output'] = str(result.output)[:1000] + "..." if len(str(result.output)) > 1000 else str(result.output)
                except:
                    result_dict['output'] = "[无法序列化]"
            serializable_results.append(result_dict)

        test_data = {
            "test_summary": {
                "total_tests": len(self.test_results),
                "passed": sum(1 for r in self.test_results if r.status == "passed"),
                "failed": sum(1 for r in self.test_results if r.status == "failed"),
                "timeout": sum(1 for r in self.test_results if r.status == "timeout"),
                "error": sum(1 for r in self.test_results if r.status == "error"),
                "total_duration": sum(r.duration for r in self.test_results)
            },
            "test_results": serializable_results,
            "test_cases": [asdict(tc) for tc in self.test_cases]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, indent=2, ensure_ascii=False)

        print(f"[SUCCESS] 测试结果已保存到: {output_file}")


def create_sample_test_cases(output_path: str):
    """创建示例测试用例文件"""
    sample_data = {
        "description": "LangGraph代理示例测试用例",
        "version": "1.0",
        "test_cases": [
            {
                "name": "basic_conversation",
                "description": "基础对话测试",
                "input_data": {
                    "messages": [{"role": "human", "content": "你好"}]
                },
                "expected_output": {
                    "contains": ["你好", "Hello"],
                    "type": "dict"
                },
                "timeout": 30.0,
                "category": "conversation"
            },
            {
                "name": "tool_usage_test",
                "description": "工具使用测试",
                "input_data": {
                    "messages": [{"role": "human", "content": "现在几点了？"}]
                },
                "expected_output": {
                    "contains": ["时间", "点", "时"],
                    "min_length": 10
                },
                "timeout": 20.0,
                "category": "tools"
            },
            {
                "name": "calculation_test",
                "description": "计算功能测试",
                "input_data": {
                    "messages": [{"role": "human", "content": "计算 123 + 456"}]
                },
                "expected_output": {
                    "contains": ["579"],
                    "type": "dict"
                },
                "timeout": 15.0,
                "category": "calculation"
            }
        ]
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2, ensure_ascii=False)

    print(f"[SUCCESS] 示例测试用例已创建: {output_path}")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangGraph代理测试框架")
    parser.add_argument("--graph", help="LangGraph图模块路径")
    parser.add_argument("--test-cases", help="测试用例JSON文件路径")
    parser.add_argument("--output", default="./test_results.json",
                       help="测试结果输出文件")
    parser.add_argument("--report", action="store_true",
                       help="生成测试报告")
    parser.add_argument("--create-sample", action="store_true",
                       help="创建示例测试用例文件")
    parser.add_argument("--sample-path", default="./sample_test_cases.json",
                       help="示例测试用例输出路径")

    args = parser.parse_args()

    print("=" * 60)
    print("LangGraph代理测试框架")
    print("=" * 60)

    if args.create_sample:
        create_sample_test_cases(args.sample_path)
        return

    if not args.graph:
        print("[ERROR] 请指定图模块路径 (--graph)")
        return

    try:
        # 动态导入图模块
        module_path = args.graph.replace('/', '.').replace('.py', '')
        graph_module = __import__(module_path, fromlist=['graph'])
        graph = getattr(graph_module, 'graph')

        print(f"[INFO] 成功加载图模块: {module_path}")

    except Exception as e:
        print(f"[ERROR] 加载图模块失败: {e}")
        return

    # 创建测试器
    tester = AgentTester(graph)

    # 加载测试用例
    if args.test_cases:
        tester.add_test_cases_from_file(args.test_cases)
    else:
        # 添加默认测试用例
        default_test_cases = [
            TestCase(
                name="default_test",
                description="默认测试",
                input_data={"messages": [{"role": "human", "content": "测试消息"}]},
                timeout=30.0
            )
        ]
        for test_case in default_test_cases:
            tester.add_test_case(test_case)

    # 运行测试
    print("[INFO] 开始运行测试...")
    results = await tester.run_all_tests()

    # 生成报告
    if args.report:
        print("\n" + "=" * 60)
        print("测试报告")
        print("=" * 60)
        report = tester.generate_test_report()
        print(report)

    # 保存结果
    tester.save_test_results(args.output)

    # 返回退出码
    failed_count = sum(1 for r in results if r.status != "passed")
    if failed_count > 0:
        print(f"\n[WARNING] 有 {failed_count} 个测试未通过")
        sys.exit(1)
    else:
        print(f"\n[SUCCESS] 所有 {len(results)} 个测试通过")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())
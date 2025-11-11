"""
计算器工具
演示如何为智能体添加数学计算能力
"""

import re
from typing import Union, Dict, Any

def safe_calculate(expression: str) -> Dict[str, Any]:
    """
    安全的数学表达式计算器

    Args:
        expression: 数学表达式，如 "2 + 3 * 4"

    Returns:
        计算结果字典
    """
    try:
        # 移除空格
        expr = expression.replace(" ", "")

        # 验证表达式只包含数字和基本运算符
        if not re.match(r'^[\d+\-*/().]+$', expr):
            return {
                "success": False,
                "error": "表达式包含不支持的字符",
                "expression": expression
            }

        # 使用eval进行计算（注意：在生产环境中应该使用更安全的数学库）
        result = eval(expr)

        # 检查结果是否为数字
        if not isinstance(result, (int, float)):
            return {
                "success": False,
                "error": "计算结果不是有效数字",
                "expression": expression
            }

        return {
            "success": True,
            "result": result,
            "expression": expression,
            "type": "number" if isinstance(result, (int, float)) else "other"
        }

    except ZeroDivisionError:
        return {
            "success": False,
            "error": "除零错误",
            "expression": expression
        }
    except SyntaxError:
        return {
            "success": False,
            "error": "表达式语法错误",
            "expression": expression
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"计算错误: {str(e)}",
            "expression": expression
        }

def format_calculation_response(calc_result: Dict[str, Any]) -> str:
    """
    格式化计算结果

    Args:
        calc_result: 计算结果字典

    Returns:
        格式化的结果字符串
    """
    if calc_result["success"]:
        return f"🧮 计算: {calc_result['expression']} = {calc_result['result']}"
    else:
        return f"❌ 计算错误: {calc_result['error']} (表达式: {calc_result['expression']})"
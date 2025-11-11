"""
LangGraph基础使用示例
展示如何快速上手LangGraph开发
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.basic_agent import run_basic_agent

if __name__ == "__main__":
    print("欢迎来到LangGraph世界！")
    print("这个示例将展示LangGraph的基础功能。")
    print("\n与Coze相比，LangGraph的优势：")
    print("1. 完全的代码控制权")
    print("2. 更灵活的状态管理")
    print("3. 更强的自定义能力")
    print("4. 更好的调试和测试支持")
    print("\n" + "="*50)

    run_basic_agent()
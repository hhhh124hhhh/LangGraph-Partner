"""
工具智能体使用示例
展示LangGraph中工具调用的完整流程
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.tools_agent import run_tools_agent

if __name__ == "__main__":
    print("🛠️  LangGraph 工具智能体演示")
    print("=" * 40)
    print("\n与Coze工具调用相比，LangGraph的优势：")
    print("✅ 完全自定义工具逻辑")
    print("✅ 更灵活的错误处理")
    print("✅ 更好的调试能力")
    print("✅ 性能优化空间大")
    print("✅ 无限制的工具集成")
    print("\n" + "=" * 40)

    run_tools_agent()
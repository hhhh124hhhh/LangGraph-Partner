#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph项目模板生成器

此脚本用于生成不同类型的LangGraph项目模板，包括基础代理、RAG系统、多代理系统等。
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List


TEMPLATES = {
    "basic_agent": {
        "description": "基础LangGraph代理模板",
        "files": {
            "src/main.py": "basic_agent_main.py",
            "src/agent.py": "basic_agent_agent.py",
            "requirements.txt": "basic_requirements.txt",
            "README.md": "basic_readme.md"
        }
    },
    "rag_system": {
        "description": "RAG系统模板",
        "files": {
            "src/main.py": "rag_main.py",
            "src/rag_agent.py": "rag_agent.py",
            "src/vector_store.py": "vector_store.py",
            "src/document_processor.py": "document_processor.py",
            "requirements.txt": "rag_requirements.txt",
            "README.md": "rag_readme.md"
        }
    },
    "multi_agent": {
        "description": "多代理系统模板",
        "files": {
            "src/main.py": "multi_agent_main.py",
            "src/supervisor.py": "supervisor.py",
            "src/agents/researcher.py": "researcher_agent.py",
            "src/agents/writer.py": "writer_agent.py",
            "src/agents/critic.py": "critic_agent.py",
            "requirements.txt": "multi_agent_requirements.txt",
            "README.md": "multi_agent_readme.md"
        }
    },
    "production_ready": {
        "description": "生产就绪模板",
        "files": {
            "src/main.py": "prod_main.py",
            "src/config.py": "prod_config.py",
            "src/monitoring.py": "prod_monitoring.py",
            "src/api_server.py": "api_server.py",
            "docker-compose.yml": "docker_compose.yml",
            "Dockerfile": "Dockerfile",
            "requirements.txt": "prod_requirements.txt",
            "README.md": "prod_readme.md"
        }
    }
}


TEMPLATE_CONTENTS = {
    "basic_agent_main.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础LangGraph代理主程序
"""

import asyncio
import os
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from agent import BasicAgent
from utils.config import load_config


async def main():
    """主函数"""
    # 加载配置
    config = load_config()

    # 创建代理
    agent = BasicAgent(config)

    # 编译图
    graph = agent.compile()

    print("基础LangGraph代理已启动")
    print("输入 'exit' 退出程序")
    print("-" * 50)

    # 主循环
    while True:
        try:
            user_input = input("用户: ")

            if user_input.lower() == 'exit':
                print("再见！")
                break

            # 运行代理
            result = await graph.ainvoke({
                "messages": [("human", user_input)]
            })

            print(f"代理: {result['messages'][-1].content}")

        except KeyboardInterrupt:
            print("\\n程序被中断")
            break
        except Exception as e:
            print(f"错误: {e}")


if __name__ == "__main__":
    asyncio.run(main())
''',

    "basic_agent_agent.py": '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础LangGraph代理实现
"""

from typing import Dict, List, Any
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI


class BasicAgent:
    """基础LangGraph代理"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = ChatOpenAI(
            model=config.get("model", "gpt-3.5-turbo"),
            temperature=config.get("temperature", 0.7)
        )

        # 初始化记忆保存器
        self.memory = MemorySaver()

    @tool
    def get_current_time(self) -> str:
        """获取当前时间"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @tool
    def calculator(self, expression: str) -> str:
        """简单计算器"""
        try:
            # 注意：生产环境中使用更安全的计算方法
            result = eval(expression)
            return f"计算结果: {result}"
        except:
            return "计算错误，请检查表达式"

    def should_continue(self, state: Dict[str, Any]) -> str:
        """决定是否继续执行工具"""
        messages = state["messages"]
        last_message = messages[-1]

        # 如果最后一条消息是工具调用，继续执行工具
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        # 否则结束
        return "end"

    def call_model(self, state: Dict[str, Any]):
        """调用语言模型"""
        messages = state["messages"]
        response = self.llm.invoke(messages)
        return {"messages": [response]}

    def call_tools(self, state: Dict[str, Any]):
        """调用工具"""
        messages = state["messages"]
        last_message = messages[-1]

        # 执行工具调用
        tool_calls = getattr(last_message, "tool_calls", [])
        if tool_calls:
            # 这里应该执行实际的工具调用
            # 为简化示例，返回工具调用结果
            results = []
            for tool_call in tool_calls:
                if tool_call["name"] == "get_current_time":
                    result = self.get_current_time()
                elif tool_call["name"] == "calculator":
                    result = self.calculator(tool_call["args"]["expression"])
                else:
                    result = "未知工具"

                results.append(AIMessage(
                    content=result,
                    tool_call_id=tool_call["id"]
                ))

            return {"messages": results}

        return {"messages": []}

    def compile(self):
        """编译图"""
        # 创建图
        workflow = StateGraph(dict)

        # 添加节点
        workflow.add_node("agent", self.call_model)
        workflow.add_node("tools", self.call_tools)

        # 添加边
        workflow.add_edge(START, "agent")
        workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "tools": "tools",
                "end": END
            }
        )
        workflow.add_edge("tools", "agent")

        # 编译图，添加记忆
        return workflow.compile(checkpointer=self.memory)
''',

    "basic_requirements.txt": '''# 核心依赖
langgraph>=0.2.0
langchain>=0.3.0
langchain-core>=0.3.0
langchain-openai>=0.2.0
langsmith>=0.1.0

# 工具和实用工具
python-dotenv>=1.0.0
pydantic>=2.0.0
typing-extensions>=4.0.0

# 异步支持
aiohttp>=3.8.0
asyncio
''',

    "basic_readme.md": '''# 基础LangGraph代理

这是一个简单的LangGraph代理模板，展示了基本的代理功能和工具调用。

## 功能特性

- 基于LangGraph的代理架构
- 支持工具调用（计算器、时间查询）
- 记忆功能，支持多轮对话
- 异步执行

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，添加你的OpenAI API密钥
```

3. 运行代理：
```bash
python src/main.py
```

## 使用示例

```
用户: 现在几点了？
代理: 现在是: 2024-01-01 12:00:00

用户: 计算 123 + 456
代理: 计算结果: 579

用户: exit
代理: 再见！
```

## 项目结构

```
├── src/
│   ├── main.py          # 主程序入口
│   ├── agent.py         # 代理实现
│   └── utils/
│       └── config.py    # 配置管理
├── requirements.txt     # 依赖列表
└── README.md           # 项目文档
```

## 自定义扩展

1. 添加新工具：在`agent.py`中的`BasicAgent`类中添加新的工具方法
2. 修改提示：调整LLM调用参数或添加系统提示
3. 扩展功能：添加更多的节点和边来扩展图的复杂性

## 注意事项

- 确保有有效的OpenAI API密钥
- 生产环境中应该使用更安全的计算方法
- 考虑添加错误处理和日志记录
''',
}


def create_template(template_name: str, output_dir: Path):
    """创建指定模板的项目"""
    if template_name not in TEMPLATES:
        print(f"[ERROR] 未知的模板: {template_name}")
        print(f"[INFO] 可用模板: {', '.join(TEMPLATES.keys())}")
        return False

    template = TEMPLATES[template_name]
    print(f"[INFO] 创建模板: {template['description']}")

    # 创建目标目录
    template_dir = output_dir / template_name
    template_dir.mkdir(parents=True, exist_ok=True)

    # 创建文件
    created_files = []
    for file_path, template_key in template["files"].items:
        full_path = template_dir / file_path

        # 确保父目录存在
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if template_key in TEMPLATE_CONTENTS:
            content = TEMPLATE_CONTENTS[template_key]
            full_path.write_text(content, encoding='utf-8')
            created_files.append(str(full_path))
        else:
            print(f"[WARNING] 模板文件 {template_key} 不存在，跳过")

    print(f"[SUCCESS] 模板创建完成，共创建 {len(created_files)} 个文件:")
    for file_path in created_files:
        print(f"  - {file_path}")

    return True


def list_templates():
    """列出所有可用模板"""
    print("可用的LangGraph项目模板:")
    print("-" * 50)
    for name, template in TEMPLATES.items():
        print(f"{name:15} - {template['description']}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangGraph项目模板生成器")
    parser.add_argument(
        "template",
        nargs="?",
        help="模板名称（basic_agent, rag_system, multi_agent, production_ready）"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="输出目录（默认为当前目录）"
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="列出所有可用模板"
    )

    args = parser.parse_args()

    # 列出模板
    if args.list:
        list_templates()
        return

    # 检查模板名称
    if not args.template:
        print("[ERROR] 请指定模板名称或使用 --list 查看可用模板")
        parser.print_help()
        return

    # 创建模板
    output_dir = Path(args.output)
    success = create_template(args.template, output_dir)

    if success:
        print("\\n" + "=" * 60)
        print("[SUCCESS] 项目模板创建成功！")
        print("=" * 60)
        print(f"\\n下一步:")
        print(f"1. cd {args.template}")
        print(f"2. 编辑配置文件")
        print(f"3. 安装依赖: pip install -r requirements.txt")
        print(f"4. 运行项目: python src/main.py")


if __name__ == "__main__":
    main()
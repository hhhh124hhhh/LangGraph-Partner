#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph学习工作室启动器

一个统一的入口，提供多种学习和开发工具
"""

import os
import sys
import time
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional
import argparse

class LangGraphStudio:
    """LangGraph学习工作室"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tools = self._setup_tools()

    def _setup_tools(self) -> Dict:
        """设置可用的工具"""
        return {
            "quick_start": {
                "title": "🚀 快速开始",
                "description": "环境检查、依赖安装和基础配置",
                "script": "quick_start.py",
                "category": "setup"
            },
            "interactive_tutorial": {
                "title": "🎓 交互式教程",
                "description": "循序渐进的学习系统，包含完整课程",
                "script": "interactive_tutorial.py",
                "category": "learning"
            },
            "demo_runner": {
                "title": "🎬 演示运行器",
                "description": "快速运行各种LangGraph演示示例",
                "script": "demo_runner.py",
                "category": "demo"
            },
            "jupyter_lab": {
                "title": "📓 Jupyter Lab",
                "description": "启动Jupyter Lab进行交互式学习",
                "script": None,
                "category": "development"
            },
            "examples": {
                "title": "📚 示例代码",
                "description": "浏览和学习完整的示例代码",
                "script": None,
                "category": "learning"
            },
            "performance_monitor": {
                "title": "📊 性能监控",
                "description": "实时监控LangGraph应用性能",
                "script": "performance_monitor.py",
                "category": "tools"
            },
            "checkpoint_analyzer": {
                "title": "🔍 检查点分析",
                "description": "分析LangGraph状态和执行历史",
                "script": "checkpoint_analyzer.py",
                "category": "tools"
            },
            "test_runner": {
                "title": "🧪 测试运行器",
                "description": "运行LangGraph应用的测试套件",
                "script": "test_agent.py",
                "category": "tools"
            }
        }

    def print_banner(self):
        """打印欢迎横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎓 LangGraph 学习工作室                     ║
║                                                              ║
║  🚀 一键启动 · 📚 渐进学习 · 🛠️ 开发工具 · 📊 性能分析         ║
║                                                              ║
║                  专为初学者设计的完整学习环境                   ║
╚══════════════════════════════════════════════════════════════╝

        """
        print(banner)

    def display_main_menu(self) -> str:
        """显示主菜单"""
        print("🎯 选择你想要的工具:")
        print()

        categories = {
            "setup": "🔧 环境设置",
            "learning": "📚 学习工具",
            "demo": "🎬 演示示例",
            "development": "🛠️ 开发环境",
            "tools": "🔧 实用工具"
        }

        menu_items = []
        current_category = None
        index = 1

        for tool_id, tool_info in self.tools.items():
            category = categories.get(tool_info["category"], "其他")

            if category != current_category:
                if current_category is not None:
                    print()
                print(f"--- {category} ---")
                current_category = category

            print(f"{index:2d}. {tool_info['title']}")
            print(f"     {tool_info['description']}")
            menu_items.append(tool_id)
            index += 1

        print()
        print(" 0. 📖 使用指南")
        print(" q. 🚪 退出工作室")

        choice = input(f"\n请选择工具 (1-{len(menu_items)}, 0, q): ").strip()

        if choice == "q":
            return "quit"
        elif choice == "0":
            return "guide"
        elif choice.isdigit() and 1 <= int(choice) <= len(menu_items):
            return menu_items[int(choice) - 1]
        else:
            return "invalid"

    def run_tool(self, tool_id: str):
        """运行指定的工具"""
        if tool_id not in self.tools:
            print(f"❌ 未知工具: {tool_id}")
            return

        tool_info = self.tools[tool_id]
        print(f"\n🚀 启动: {tool_info['title']}")
        print("=" * 60)
        print(f"📝 {tool_info['description']}")
        print()

        try:
            if tool_info["script"]:
                self.run_script(tool_info["script"])
            else:
                self.run_builtin_tool(tool_id)

        except KeyboardInterrupt:
            print("\n\n👋 工具已停止")
        except Exception as e:
            print(f"\n❌ 工具运行失败: {e}")

    def run_script(self, script_name: str):
        """运行Python脚本"""
        script_path = self.project_root / "scripts" / script_name

        if not script_path.exists():
            print(f"❌ 脚本不存在: {script_path}")
            return

        print(f"📂 执行脚本: {script_path}")
        print("-" * 40)

        try:
            # 运行脚本
            result = subprocess.run([sys.executable, str(script_path)],
                                  cwd=self.project_root,
                                  check=False)

            if result.returncode == 0:
                print("✅ 脚本执行完成")
            else:
                print("⚠️ 脚本执行时出现错误")

        except Exception as e:
            print(f"❌ 脚本执行失败: {e}")

    def run_builtin_tool(self, tool_id: str):
        """运行内置工具"""
        if tool_id == "jupyter_lab":
            self.start_jupyter_lab()
        elif tool_id == "examples":
            self.show_examples()
        else:
            print(f"❌ 未知内置工具: {tool_id}")

    def start_jupyter_lab(self):
        """启动Jupyter Lab"""
        print("🚀 启动Jupyter Lab...")

        notebooks_dir = self.project_root / "notebooks"
        notebooks_dir.mkdir(exist_ok=True)

        try:
            # 启动Jupyter Lab
            subprocess.Popen([
                sys.executable, "-m", "jupyter", "lab",
                str(notebooks_dir),
                "--browser", "new",
                "--port=8888"
            ])

            print("✅ Jupyter Lab正在启动...")
            print("📂 目录:", notebooks_dir)
            print("🌐 访问地址: http://localhost:8888")
            print("\n💡 提示: 浏览器应该会自动打开，如果没有请手动访问上述地址")

        except Exception as e:
            print(f"❌ 启动Jupyter Lab失败: {e}")
            print("请确保已安装jupyter和jupyterlab")
            print("安装命令: pip install jupyter jupyterlab")

    def show_examples(self):
        """显示示例代码"""
        examples_dir = self.project_root / "examples"

        if not examples_dir.exists():
            print("❌ 示例目录不存在")
            print("请先运行快速开始工具来创建示例")
            return

        print("📚 LangGraph示例代码:")
        print("=" * 40)

        examples = list(examples_dir.glob("*.py"))
        if not examples:
            print("暂无示例文件")
            return

        for i, example_file in enumerate(examples, 1):
            print(f"\n{i}. 📄 {example_file.name}")

            # 读取文件的前几行作为描述
            try:
                with open(example_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # 查找描述注释
                description = ""
                for line in lines[:20]:
                    if '"""' in line:
                        desc_lines = []
                        for j in range(lines.index(line) + 1, len(lines)):
                            if '"""' in lines[j]:
                                break
                            desc_lines.append(lines[j].strip().lstrip('# '))
                        description = " ".join(desc_lines)
                        break

                if description:
                    print(f"   📝 {description}")
                else:
                    print(f"   📁 大小: {example_file.stat().st_size} bytes")

            except Exception as e:
                print(f"   ⚠️ 读取失败: {e}")

        print(f"\n📂 示例目录: {examples_dir}")

        # 询问是否要运行某个示例
        try:
            choice = input("\n是否要运行某个示例? (输入数字回车查看，0返回): ").strip()
            if choice.isdigit():
                index = int(choice) - 1
                if 0 <= index < len(examples):
                    self.run_example(examples[index])
        except (ValueError, KeyboardInterrupt):
            pass

    def run_example(self, example_file: Path):
        """运行示例文件"""
        print(f"\n🚀 运行示例: {example_file.name}")
        print("-" * 40)

        try:
            result = subprocess.run([sys.executable, str(example_file)],
                                  capture_output=True, text=True,
                                  timeout=30)

            if result.returncode == 0:
                print("✅ 运行成功:")
                if result.stdout:
                    print(result.stdout)
            else:
                print("❌ 运行失败:")
                if result.stderr:
                    print(result.stderr)

        except subprocess.TimeoutExpired:
            print("⏰ 运行超时")
        except Exception as e:
            print(f"❌ 运行失败: {e}")

        input("\n按回车键继续...")

    def show_guide(self):
        """显示使用指南"""
        guide = """
📖 LangGraph学习工作室使用指南

🎯 快速开始:
1. 首次使用请选择 "🚀 快速开始" 来检查环境和安装依赖
2. 然后可以运行 "🎬 演示运行器" 体验LangGraph功能
3. 使用 "🎓 交互式教程" 进行系统性学习

📚 学习路径:
┌─────────────────────┐
│  快速开始 (环境设置)  │ → 📖 交互式教程 → 🎬 演示运行器
└─────────────────────┘

🛠️ 开发工具:
- Jupyter Lab: 交互式编程环境
- 性能监控: 实时性能分析
- 检查点分析: 状态和执行历史
- 测试运行器: 自动化测试

💡 使用技巧:
- 所有工具都支持 Ctrl+C 中断
- Jupyter Lab会自动在浏览器中打开
- 示例代码可以在examples目录中找到
- 建议按顺序完成交互式教程

🔧 故障排除:
- 如果工具运行失败，请先运行快速开始检查环境
- 确保Python版本 >= 3.9
- 检查是否安装了所需依赖
- 查看错误信息获取详细帮助

📞 获取帮助:
- 查看项目README文件
- 浏览examples目录中的代码
- 使用checkpoint_analyzer分析问题
        """

        print(guide)
        input("\n按回车键返回主菜单...")

    def check_environment(self):
        """检查环境状态"""
        print("🔍 环境状态检查")
        print("=" * 40)

        # Python版本
        version = sys.version_info
        print(f"Python版本: {version.major}.{version.minor}.{version.micro}")
        if version >= (3, 9):
            print("✅ Python版本符合要求")
        else:
            print("❌ Python版本过低，需要 >= 3.9")

        # 关键依赖
        dependencies = [
            ("langgraph", "LangGraph核心库"),
            ("langchain", "LangChain库"),
            ("jupyter", "Jupyter Notebook"),
            ("rich", "Rich终端库"),
            ("python-dotenv", "环境变量管理")
        ]

        for package, description in dependencies:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {description}")
            except ImportError:
                print(f"❌ {description} (未安装)")

        # 项目结构
        required_dirs = ["scripts", "examples", "notebooks"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                print(f"✅ {dir_name}/ 目录存在")
            else:
                print(f"❌ {dir_name}/ 目录不存在")

        # 环境文件
        env_file = self.project_root / ".env"
        if env_file.exists():
            print("✅ .env 环境文件存在")
        else:
            print("⚠️ .env 环境文件不存在")

    def run(self, auto_tool: Optional[str] = None):
        """运行工作室"""
        self.print_banner()

        if auto_tool:
            if auto_tool in self.tools:
                self.run_tool(auto_tool)
            else:
                print(f"❌ 未知工具: {auto_tool}")
            return

        while True:
            try:
                choice = self.display_main_menu()

                if choice == "quit":
                    print("\n👋 感谢使用LangGraph学习工作室!")
                    break
                elif choice == "guide":
                    self.show_guide()
                elif choice == "invalid":
                    print("❌ 无效的选择，请重试")
                else:
                    self.run_tool(choice)

                if choice not in ["quit", "invalid"]:
                    input("\n按回车键返回主菜单...")

            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="LangGraph学习工作室")
    parser.add_argument("--tool", help="直接启动指定工具")
    parser.add_argument("--check", action="store_true", help="检查环境状态")
    parser.add_argument("--version", action="store_true", help="显示版本信息")

    args = parser.parse_args()

    studio = LangGraphStudio()

    if args.version:
        print("LangGraph学习工作室 v1.0")
        return

    if args.check:
        studio.check_environment()
        return

    studio.run(auto_tool=args.tool)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph交互式教程启动器

提供渐进式的学习体验，通过交互式菜单引导用户学习LangGraph
的核心概念和实际应用。
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional
import json

class InteractiveTutorial:
    """交互式教程管理器"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.tutorials = self._load_tutorials()
        self.progress_file = self.project_root / "tutorial_progress.json"

    def _load_tutorials(self) -> Dict:
        """加载教程配置"""
        return {
            "basics": {
                "title": "📖 LangGraph基础概念",
                "description": "学习LangGraph的核心概念和基本用法",
                "lessons": [
                    {
                        "id": "hello_world",
                        "title": "Hello World",
                        "description": "创建你的第一个LangGraph应用",
                        "file": "examples/hello_world.py",
                        "difficulty": "⭐",
                        "time": "10分钟"
                    },
                    {
                        "id": "state_management",
                        "title": "状态管理",
                        "description": "理解LangGraph中的状态传递机制",
                        "file": "examples/simple_chatbot.py",
                        "difficulty": "⭐⭐",
                        "time": "15分钟"
                    },
                    {
                        "id": "conditional_routing",
                        "title": "条件路由",
                        "description": "学习如何根据条件控制工作流",
                        "file": "examples/conditional_flow.py",
                        "difficulty": "⭐⭐",
                        "time": "20分钟"
                    }
                ]
            },
            "intermediate": {
                "title": "🚀 中级技能",
                "description": "掌握更复杂的LangGraph模式和技术",
                "lessons": [
                    {
                        "id": "memory_persistence",
                        "title": "持久化内存",
                        "description": "使用检查点保存和恢复状态",
                        "file": "notebooks/03_memory_persistence.ipynb",
                        "difficulty": "⭐⭐⭐",
                        "time": "25分钟"
                    },
                    {
                        "id": "tool_integration",
                        "title": "工具集成",
                        "description": "集成外部工具和API",
                        "file": "notebooks/04_tools_and_agents.ipynb",
                        "difficulty": "⭐⭐⭐",
                        "time": "30分钟"
                    },
                    {
                        "id": "error_handling",
                        "title": "错误处理",
                        "description": "构建健壮的LangGraph应用",
                        "file": "notebooks/05_error_handling.ipynb",
                        "difficulty": "⭐⭐⭐",
                        "time": "25分钟"
                    }
                ]
            },
            "advanced": {
                "title": "💡 高级应用",
                "description": "探索企业级的LangGraph架构模式",
                "lessons": [
                    {
                        "id": "multi_agent",
                        "title": "多代理系统",
                        "description": "构建协作的多代理应用",
                        "file": "notebooks/06_multi_agent_systems.ipynb",
                        "difficulty": "⭐⭐⭐⭐",
                        "time": "40分钟"
                    },
                    {
                        "id": "human_in_loop",
                        "title": "人机协作",
                        "description": "在循环中集成人类决策",
                        "file": "notebooks/07_human_in_loop.ipynb",
                        "difficulty": "⭐⭐⭐⭐",
                        "time": "35分钟"
                    },
                    {
                        "id": "production_deployment",
                        "title": "生产部署",
                        "description": "将LangGraph应用部署到生产环境",
                        "file": "notebooks/08_production_deployment.ipynb",
                        "difficulty": "⭐⭐⭐⭐⭐",
                        "time": "45分钟"
                    }
                ]
            }
        }

    def load_progress(self) -> Dict:
        """加载学习进度"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"completed_lessons": [], "current_lesson": None, "start_time": None}

    def save_progress(self, progress: Dict):
        """保存学习进度"""
        try:
            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存进度失败: {e}")

    def display_welcome(self):
        """显示欢迎界面"""
        print("""
🎓 欢迎使用LangGraph交互式教程系统

本系统将引导你循序渐进地学习LangGraph，从基础概念到高级应用。

📚 教程特点:
• 🎯 渐进式学习路径
• 💻 互动式代码示例
• 📊 实时进度跟踪
• 🛠️ 实践导向项目
        """)

    def display_main_menu(self) -> str:
        """显示主菜单"""
        progress = self.load_progress()
        completed_count = len(progress.get("completed_lessons", []))

        print(f"\n📊 学习进度: {completed_count} 个课程已完成")
        print("\n" + "="*60)
        print("请选择学习模块:")
        print("0. 🏠 查看学习进度")
        print("1. 📖 LangGraph基础概念")
        print("2. 🚀 中级技能")
        print("3. 💡 高级应用")
        print("4. 🎯 快速挑战")
        print("5. 🛠️ 实践项目")
        print("6. ⚙️ 系统设置")
        print("q. 🚪 退出")

        return input("\n请输入选择 (0-6, q): ").strip()

    def display_module_menu(self, module_key: str) -> str:
        """显示模块菜单"""
        module = self.tutorials[module_key]
        progress = self.load_progress()
        completed = progress.get("completed_lessons", [])

        print(f"\n{module['title']}")
        print("=" * len(module['title']))
        print(f"{module['description']}\n")

        for i, lesson in enumerate(module["lessons"], 1):
            status = "✅" if lesson["id"] in completed else "⭕"
            print(f"{i}. {status} {lesson['title']} ({lesson['difficulty']})")
            print(f"   {lesson['description']}")
            print(f"   ⏱️  {lesson['time']}")
            print()

        print("0. 🔙 返回主菜单")
        return input("请选择课程 (0-{}): ".format(len(module["lessons"]))).strip()

    def run_lesson(self, module_key: str, lesson_index: int):
        """运行课程"""
        module = self.tutorials[module_key]
        lessons = module["lessons"]

        if lesson_index < 0 or lesson_index >= len(lessons):
            print("❌ 无效的课程选择")
            return

        lesson = lessons[lesson_index]
        lesson_file = self.project_root / lesson["file"]

        print(f"\n🎯 开始学习: {lesson['title']}")
        print("=" * 50)
        print(f"📝 描述: {lesson['description']}")
        print(f"📁 文件: {lesson['file']}")
        print(f"⭐ 难度: {lesson['difficulty']}")
        print(f"⏱️  预计时间: {lesson['time']}")

        if not lesson_file.exists():
            print(f"❌ 文件不存在: {lesson_file}")
            print("正在创建文件...")
            self.create_missing_lesson(lesson)
            return

        # 根据文件类型选择运行方式
        if lesson_file.suffix == '.py':
            self.run_python_lesson(lesson_file, lesson)
        elif lesson_file.suffix == '.ipynb':
            self.run_jupyter_lesson(lesson_file, lesson)
        else:
            print(f"❌ 不支持的文件类型: {lesson_file.suffix}")

        # 更新进度
        self.mark_lesson_completed(lesson["id"])

    def create_missing_lesson(self, lesson: Dict):
        """创建缺失的课程文件"""
        if lesson["id"] == "hello_world":
            # 已在quick_start.py中创建
            print("✅ Hello World课程文件已存在")
        elif lesson["id"] == "state_management":
            # 已在quick_start.py中创建
            print("✅ 状态管理课程文件已存在")
        elif lesson["id"] == "conditional_routing":
            # 已在quick_start.py中创建
            print("✅ 条件路由课程文件已存在")
        else:
            # 创建Jupyter notebook占位符
            self.create_notebook_placeholder(lesson)

    def create_notebook_placeholder(self, lesson: Dict):
        """创建Jupyter notebook占位符"""
        notebook_dir = self.project_root / "notebooks"
        notebook_dir.mkdir(exist_ok=True)

        notebook_content = {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# {lesson['title']}\n\n",
                        f"{lesson['description']}\n\n",
                        f"**难度**: {lesson['difficulty']}\n\n",
                        f"**预计时间**: {lesson['time']}\n\n",
                        "---\n\n",
                        "## 课程内容\n\n",
                        "### 学习目标\n\n",
                        "通过本课程，你将学习到:\n\n",
                        "- [目标1]\n",
                        "- [目标2]\n",
                        "- [目标3]\n\n",
                        "### 实践练习\n\n",
                        "下面让我们开始实践...\n\n",
                        "```python\n",
                        "# 在这里编写你的代码\n",
                        "```\n\n",
                        "### 总结\n\n",
                        "完成本课程后，你应该能够:\n\n",
                        "- [技能1]\n",
                        "- [技能2]\n"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "codemirror_mode": {
                        "name": "ipython",
                        "version": 3
                    },
                    "file_extension": ".py",
                    "mimetype": "text/x-python",
                    "name": "python",
                    "nbconvert_exporter": "python",
                    "pygments_lexer": "ipython3",
                    "version": "3.9.0"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }

        notebook_file = self.project_root / lesson["file"]
        notebook_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            import json
            with open(notebook_file, 'w', encoding='utf-8') as f:
                json.dump(notebook_content, f, indent=2)
            print(f"✅ 创建了Jupyter notebook: {notebook_file}")
        except ImportError:
            print("❌ 需要安装json库来创建notebook")
        except Exception as e:
            print(f"❌ 创建notebook失败: {e}")

    def run_python_lesson(self, file_path: Path, lesson: Dict):
        """运行Python课程"""
        print(f"\n🚀 运行Python课程: {file_path}")
        print("-" * 40)

        try:
            # 询问用户是否要运行代码
            choice = input("是否运行此课程代码? (y/n): ").strip().lower()

            if choice in ['y', 'yes', '是']:
                print("🏃‍♂️ 执行中...")
                result = subprocess.run([sys.executable, str(file_path)],
                                      capture_output=True, text=True, timeout=60)

                if result.returncode == 0:
                    print("✅ 执行成功!")
                    if result.stdout:
                        print("输出:")
                        print(result.stdout)
                else:
                    print("❌ 执行失败:")
                    if result.stderr:
                        print("错误信息:")
                        print(result.stderr)

            # 询问是否要查看代码
            choice = input("是否查看课程代码? (y/n): ").strip().lower()
            if choice in ['y', 'yes', '是']:
                print("\n📄 课程代码:")
                print("=" * 40)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 限制显示行数
                        lines = content.split('\n')
                        if len(lines) > 50:
                            print("(显示前50行)")
                            print('\n'.join(lines[:50]))
                            print(f"...(还有{len(lines)-50}行)")
                        else:
                            print(content)
                except Exception as e:
                    print(f"读取文件失败: {e}")

        except subprocess.TimeoutExpired:
            print("⏰ 代码执行超时")
        except Exception as e:
            print(f"❌ 运行课程失败: {e}")

    def run_jupyter_lesson(self, file_path: Path, lesson: Dict):
        """运行Jupyter课程"""
        print(f"\n📓 Jupyter Notebook课程: {file_path}")

        try:
            choice = input("是否在Jupyter中打开此notebook? (y/n): ").strip().lower()

            if choice in ['y', 'yes', '是']:
                print("🚀 启动Jupyter...")
                subprocess.run([
                    sys.executable, "-m", "jupyter", "notebook",
                    str(file_path),
                    "--browser", "new"
                ])
                print("✅ Jupyter已启动")
        except Exception as e:
            print(f"❌ 启动Jupyter失败: {e}")

    def mark_lesson_completed(self, lesson_id: str):
        """标记课程为已完成"""
        progress = self.load_progress()
        if lesson_id not in progress.get("completed_lessons", []):
            progress["completed_lessons"].append(lesson_id)
            self.save_progress(progress)
            print("✅ 课程已完成，进度已保存!")

    def display_progress(self):
        """显示学习进度"""
        progress = self.load_progress()
        completed = progress.get("completed_lessons", [])
        total_lessons = sum(len(module["lessons"]) for module in self.tutorials.values())

        print("\n📊 学习进度报告")
        print("=" * 50)
        print(f"已完成课程: {len(completed)}/{total_lessons}")

        if total_lessons > 0:
            percentage = (len(completed) / total_lessons) * 100
            print(f"完成百分比: {percentage:.1f}%")

            # 显示进度条
            bar_length = 30
            filled_length = int(bar_length * percentage / 100)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            print(f"进度条: [{bar}]")

        print("\n📋 已完成课程:")
        if completed:
            for lesson_id in completed:
                print(f"✅ {lesson_id}")
        else:
            print("   还没有完成任何课程")

        print("\n🎯 建议下一步:")
        if not completed:
            print("   建议从 '📖 LangGraph基础概念' 开始学习")
        else:
            # 找到下一个未完成的课程
            for module_key, module in self.tutorials.items():
                for lesson in module["lessons"]:
                    if lesson["id"] not in completed:
                        print(f"   建议学习: {lesson['title']} ({module['title']})")
                        break
                else:
                    continue
                break

    def quick_challenge(self):
        """快速挑战"""
        challenges = [
            {
                "title": "🧮 数学计算器",
                "description": "创建一个能处理四则运算的计算器",
                "hint": "使用条件路由和正则表达式提取数字",
                "difficulty": "⭐"
            },
            {
                "title": "🌤️ 天气助手",
                "description": "创建一个天气查询助手（模拟）",
                "hint": "使用状态管理保存用户位置信息",
                "difficulty": "⭐⭐"
            },
            {
                "title": "🤖 智能客服",
                "description": "创建一个简单的人工客服机器人",
                "hint": "结合条件路由和记忆功能",
                "difficulty": "⭐⭐⭐"
            }
        ]

        print("\n🎯 快速挑战")
        print("=" * 40)
        print("选择一个挑战来测试你的技能:")

        for i, challenge in enumerate(challenges, 1):
            print(f"\n{i}. {challenge['title']} ({challenge['difficulty']})")
            print(f"   {challenge['description']}")
            print(f"   💡 提示: {challenge['hint']}")

        print("\n0. 🔙 返回主菜单")

        choice = input("选择挑战 (0-{}): ".format(len(challenges))).strip()

        if choice == "0":
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(challenges):
                challenge = challenges[index]
                self.run_challenge(challenge)
        except ValueError:
            print("❌ 无效的选择")

    def run_challenge(self, challenge: Dict):
        """运行挑战"""
        print(f"\n🎯 挑战: {challenge['title']}")
        print("=" * 50)
        print(f"📝 描述: {challenge['description']}")
        print(f"💡 提示: {challenge['hint']}")

        # 创建挑战目录
        challenge_dir = self.project_root / "challenges"
        challenge_dir.mkdir(exist_ok=True)

        challenge_file = challenge_dir / f"{challenge['title'].replace(' ', '_').replace('🧮', '').replace('🌤️', '').replace('🤖', '')}.py"

        choice = input("\n是否要开始编写挑战代码? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            try:
                # 启动默认编辑器
                if os.name == 'nt':  # Windows
                    os.startfile(challenge_file)
                else:  # Unix-like
                    subprocess.run(['nano', str(challenge_file)])
                print(f"✅ 已打开编辑器: {challenge_file}")
            except Exception as e:
                print(f"❌ 打开编辑器失败: {e}")
                print(f"请手动编辑文件: {challenge_file}")

    def practice_projects(self):
        """实践项目"""
        projects = [
            {
                "title": "💬 智能聊天机器人",
                "description": "创建一个具有记忆和多轮对话能力的聊天机器人",
                "skills": ["状态管理", "持久化内存", "对话逻辑"],
                "difficulty": "⭐⭐⭐"
            },
            {
                "title": "📊 数据分析助手",
                "description": "构建一个能处理和分析数据的AI助手",
                "skills": ["工具集成", "数据处理", "报告生成"],
                "difficulty": "⭐⭐⭐⭐"
            },
            {
                "title": "🔍 多代理研究系统",
                "description": "创建一个协作式的研究助手系统",
                "skills": ["多代理架构", "任务分配", "结果整合"],
                "difficulty": "⭐⭐⭐⭐⭐"
            }
        ]

        print("\n🛠️ 实践项目")
        print("=" * 40)
        print("通过完整的项目实践你的技能:")

        for i, project in enumerate(projects, 1):
            print(f"\n{i}. {project['title']} ({project['difficulty']})")
            print(f"   {project['description']}")
            print(f"   🛠️  技能: {', '.join(project['skills'])}")

        print("\n0. 🔙 返回主菜单")

        choice = input("选择项目 (0-{}): ".format(len(projects))).strip()

        if choice == "0":
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(projects):
                project = projects[index]
                self.start_project(project)
        except ValueError:
            print("❌ 无效的选择")

    def start_project(self, project: Dict):
        """开始项目"""
        print(f"\n🛠️ 项目: {project['title']}")
        print("=" * 50)
        print(f"📝 描述: {project['description']}")
        print(f"🛠️  涉及技能: {', '.join(project['skills'])}")

        project_dir = self.project_root / "projects" / project['title'].replace(' ', '_')
        project_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n📁 项目目录: {project_dir}")
        print("🚀 项目已初始化，开始你的实践吧!")

        choice = input("\n是否要打开项目目录? (y/n): ").strip().lower()
        if choice in ['y', 'yes', '是']:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(project_dir)
                else:  # Unix-like
                    subprocess.run(['xdg-open', str(project_dir)])
                print("✅ 项目目录已打开")
            except Exception as e:
                print(f"❌ 打开目录失败: {e}")

    def system_settings(self):
        """系统设置"""
        print("\n⚙️ 系统设置")
        print("=" * 40)
        print("1. 🗑️  清除学习进度")
        print("2. 📊 导出学习报告")
        print("3. 🔧 检查环境")
        print("0. 🔙 返回主菜单")

        choice = input("选择设置 (0-3): ").strip()

        if choice == "1":
            if input("确定要清除所有学习进度吗? (y/n): ").strip().lower() in ['y', 'yes']:
                if self.progress_file.exists():
                    self.progress_file.unlink()
                print("✅ 学习进度已清除")
        elif choice == "2":
            self.export_progress_report()
        elif choice == "3":
            self.check_environment()

    def export_progress_report(self):
        """导出学习进度报告"""
        progress = self.load_progress()
        report_file = self.project_root / "learning_report.md"

        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# LangGraph学习报告\n\n")
                f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write(f"已完成课程: {len(progress.get('completed_lessons', []))}\n\n")

                if progress.get('completed_lessons'):
                    f.write("## 已完成课程\n\n")
                    for lesson_id in progress['completed_lessons']:
                        f.write(f"- ✅ {lesson_id}\n")

            print(f"✅ 学习报告已导出到: {report_file}")
        except Exception as e:
            print(f"❌ 导出失败: {e}")

    def check_environment(self):
        """检查环境"""
        print("\n🔍 环境检查")
        print("=" * 40)

        # 检查Python版本
        version = sys.version_info
        print(f"Python版本: {version.major}.{version.minor}.{version.micro}")

        # 检查关键依赖
        dependencies = ["langgraph", "langchain", "jupyter"]
        for dep in dependencies:
            try:
                __import__(dep)
                print(f"✅ {dep} 已安装")
            except ImportError:
                print(f"❌ {dep} 未安装")

    def run(self):
        """运行交互式教程"""
        self.display_welcome()

        while True:
            try:
                choice = self.display_main_menu()

                if choice == "q":
                    print("\n👋 感谢使用LangGraph交互式教程!")
                    break
                elif choice == "0":
                    self.display_progress()
                elif choice == "1":
                    module_choice = self.display_module_menu("basics")
                    if module_choice != "0":
                        self.run_lesson("basics", int(module_choice) - 1)
                elif choice == "2":
                    module_choice = self.display_module_menu("intermediate")
                    if module_choice != "0":
                        self.run_lesson("intermediate", int(module_choice) - 1)
                elif choice == "3":
                    module_choice = self.display_module_menu("advanced")
                    if module_choice != "0":
                        self.run_lesson("advanced", int(module_choice) - 1)
                elif choice == "4":
                    self.quick_challenge()
                elif choice == "5":
                    self.practice_projects()
                elif choice == "6":
                    self.system_settings()
                else:
                    print("❌ 无效的选择，请重试")

                if choice != "q":
                    input("\n按回车键继续...")

            except KeyboardInterrupt:
                print("\n\n👋 再见!")
                break
            except Exception as e:
                print(f"\n❌ 发生错误: {e}")
                input("按回车键继续...")

def main():
    """主函数"""
    tutorial = InteractiveTutorial()
    tutorial.run()

if __name__ == "__main__":
    main()
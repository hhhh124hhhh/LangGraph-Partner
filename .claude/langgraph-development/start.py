#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph学习环境一键启动脚本

这是最简单的启动方式，适合完全的初学者使用。
只需运行这个脚本，就能开始学习LangGraph！
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def print_welcome():
    """打印欢迎信息"""
    welcome = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          欢迎来到 LangGraph 学习环境！                        ║
║                                                              ║
║    这个脚本将帮助你快速开始学习LangGraph                        ║
║                                                              ║
║    零配置启动 · 完整教程 · 实用工具                           ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

    """
    print(welcome)

def check_python_version():
    """检查Python版本"""
    version = sys.version_info
    if version >= (3, 9):
        print(f"[OK] Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[ERROR] Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要Python 3.9或更高版本")
        return False

def show_main_menu():
    """显示主菜单"""
    print("\n" + "="*60)
    print("选择你的学习方式:")
    print()
    print("1. 快速体验 - 立即运行LangGraph演示")
    print("2. 系统学习 - 完整的交互式教程")
    print("3. 开发工具 - Jupyter和代码编辑器")
    print("4. 学习资料 - 查看文档和示例")
    print("5. 环境检查 - 检查安装和配置")
    print("6. 新手指南 - 查看完整使用指南")
    print()
    print("q. 退出")
    print()

    return input("请输入选择 (1-6, q): ").strip()

def quick_demo():
    """快速演示"""
    print("\n启动快速演示...")
    try:
        # 运行演示运行器
        subprocess.run([sys.executable, "scripts/demo_runner.py"], check=False)
    except Exception as e:
        print(f"启动失败: {e}")
        print("请确保你在正确的目录中运行此脚本")

def interactive_learning():
    """交互式学习"""
    print("\n启动交互式学习系统...")
    try:
        subprocess.run([sys.executable, "scripts/interactive_tutorial.py"], check=False)
    except Exception as e:
        print(f"启动失败: {e}")

def development_tools():
    """开发工具"""
    print("\n开发工具菜单:")
    print("1. 启动Jupyter Lab")
    print("2. 打开示例代码目录")
    print("3. 启动完整工作室")
    print("0. 返回主菜单")

    choice = input("请选择 (1-3, 0): ").strip()

    if choice == "1":
        start_jupyter()
    elif choice == "2":
        open_examples()
    elif choice == "3":
        start_studio()
    elif choice == "0":
        return

def start_jupyter():
    """启动Jupyter Lab"""
    print("\n启动Jupyter Lab...")
    try:
        notebooks_dir = Path("notebooks")
        notebooks_dir.mkdir(exist_ok=True)

        print("启动中，请稍候...")
        subprocess.Popen([
            sys.executable, "-m", "jupyter", "lab",
            str(notebooks_dir),
            "--browser", "new"
        ])
        print("Jupyter Lab已启动!")
        print("访问: http://localhost:8888")
    except Exception as e:
        print(f"启动失败: {e}")
        print("请安装jupyter: pip install jupyter jupyterlab")

def open_examples():
    """打开示例目录"""
    examples_dir = Path("examples")
    if examples_dir.exists():
        print(f"📂 示例目录: {examples_dir.absolute()}")
        try:
            # 尝试用系统默认方式打开目录
            if os.name == 'nt':  # Windows
                os.startfile(examples_dir)
            else:  # macOS/Linux
                subprocess.run(['xdg-open', str(examples_dir)])
            print("✅ 目录已在文件管理器中打开")
        except:
            print("请手动打开示例目录查看代码示例")
    else:
        print("❌ 示例目录不存在")
        print("请先运行环境检查来创建示例文件")

def start_studio():
    """启动完整工作室"""
    print("\n🚀 启动LangGraph学习工作室...")
    try:
        subprocess.run([sys.executable, "scripts/launch_studio.py"], check=False)
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def learning_resources():
    """学习资源"""
    print("\n📚 LangGraph学习资源")
    print("=" * 50)

    resources = [
        ("📖 完整新手指南", "docs/beginner_guide.md"),
        ("📚 API参考手册", "references/api_reference.md"),
        ("🏗️ 架构模式指南", "references/architecture_patterns.md"),
        ("💻 示例代码", "examples/"),
        ("📓 Jupyter教程", "notebooks/"),
        ("🔧 实用工具", "scripts/")
    ]

    for name, path in resources:
        full_path = Path(path)
        if full_path.exists():
            if full_path.is_file():
                size = full_path.stat().st_size
                print(f"✅ {name} ({path}) - {size} bytes")
            else:
                print(f"✅ {name} ({path}) - 目录")
        else:
            print(f"❌ {name} ({path}) - 不存在")

    print(f"\n📂 项目根目录: {Path().absolute()}")

    choice = input("\n是否打开新手指南? (y/n): ").strip().lower()
    if choice in ['y', 'yes', '是']:
        try:
            guide_file = Path("docs/beginner_guide.md")
            if guide_file.exists():
                if os.name == 'nt':  # Windows
                    os.startfile(guide_file)
                else:
                    subprocess.run(['xdg-open', str(guide_file)])
                print("✅ 新手指南已打开")
        except Exception as e:
            print(f"❌ 打开失败: {e}")

def environment_check():
    """环境检查"""
    print("\n🔧 环境检查")
    print("=" * 50)

    # 检查Python版本
    python_ok = check_python_version()

    # 检查关键依赖
    dependencies = [
        ("langgraph", "LangGraph核心库"),
        ("langchain", "LangChain库"),
        ("jupyter", "Jupyter Notebook"),
        ("rich", "Rich终端库"),
        ("python-dotenv", "环境变量管理")
    ]

    print("\n📦 依赖检查:")
    all_deps_ok = True
    for package, description in dependencies:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} (未安装)")
            all_deps_ok = False

    # 检查项目结构
    print("\n📁 项目结构:")
    required_dirs = ["scripts", "examples", "notebooks", "docs", "references"]
    structure_ok = True
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"✅ {dir_name}/ 目录存在")
        else:
            print(f"❌ {dir_name}/ 目录不存在")
            structure_ok = False

    # 检查环境文件
    print("\n🔑 环境配置:")
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env 环境文件存在")

        # 检查API密钥
        try:
            from dotenv import load_dotenv
            load_dotenv()
            if os.getenv("OPENAI_API_KEY"):
                print("✅ OpenAI API密钥已设置")
            else:
                print("⚠️ OpenAI API密钥未设置")
        except ImportError:
            print("⚠️ python-dotenv未安装，无法检查API密钥")
    else:
        print("❌ .env 环境文件不存在")

    # 总结
    print("\n" + "="*50)
    if python_ok and all_deps_ok and structure_ok:
        print("🎉 环境检查通过！可以开始学习LangGraph了！")
    else:
        print("⚠️ 环境存在问题，建议运行以下命令:")
        print("   python scripts/quick_start.py")
        print("   这将自动修复大多数问题")

    input("\n按回车键继续...")

def show_beginner_guide():
    """显示新手指南摘要"""
    print("\n📖 LangGraph新手指南摘要")
    print("=" * 50)

    guide_summary = """
🎯 什么是LangGraph？
LangGraph是构建有状态、多步骤AI应用的强大框架。
你可以像搭积木一样组合不同的AI功能，创建智能工作流。

⚡ 快速开始:
1. 运行环境检查确保安装正确
2. 尝试快速演示体验功能
3. 使用交互式教程系统学习
4. 查看示例代码学习实践

📚 核心概念:
- 图（Graph）: 节点和边的集合
- 节点（Node）: 执行任务的函数
- 边（Edge）: 连接节点，定义数据流
- 状态（State）: 在节点间传递的数据

🛠️ 两种主要图类型:
- StateGraph: 复杂状态管理（最常用）
- MessageGraph: 简单消息流处理

🚀 学习路径:
1. 基础概念 → 2. 核心技能 → 3. 高级特性

💡 实用技巧:
- 使用异步操作提高性能
- 避免在节点中使用阻塞调用
- 合理使用状态管理
- 充分利用错误处理

🔧 获取帮助:
- 查看docs/beginner_guide.md完整指南
- 运行python scripts/launch_studio.py使用所有工具
- 浏览examples/目录中的示例代码
    """

    print(guide_summary)

    choice = input("\n是否查看完整新手指南? (y/n): ").strip().lower()
    if choice in ['y', 'yes', '是']:
        try:
            guide_file = Path("docs/beginner_guide.md")
            if guide_file.exists():
                if os.name == 'nt':  # Windows
                    os.startfile(guide_file)
                else:
                    subprocess.run(['xdg-open', str(guide_file)])
                print("✅ 完整指南已打开")
            else:
                print("❌ 新手指南文件不存在")
        except Exception as e:
            print(f"❌ 打开失败: {e}")

def main():
    """主函数"""
    print_welcome()

    # 检查是否在正确的目录
    required_files = ["scripts/quick_start.py", "docs/beginner_guide.md"]
    missing_files = [f for f in required_files if not Path(f).exists()]

    if missing_files:
        print("❌ 当前目录不正确或文件缺失")
        print(f"缺失文件: {missing_files}")
        print("请确保你在LangGraph项目根目录中运行此脚本")
        return

    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return

    while True:
        try:
            choice = show_main_menu()

            if choice == "q":
                print("\n👋 感谢使用LangGraph学习环境!")
                print("   祝你学习愉快！")
                break
            elif choice == "1":
                quick_demo()
            elif choice == "2":
                interactive_learning()
            elif choice == "3":
                development_tools()
            elif choice == "4":
                learning_resources()
            elif choice == "5":
                environment_check()
            elif choice == "6":
                show_beginner_guide()
            else:
                print("❌ 无效的选择，请重试")

            if choice != "q":
                input("\n按回车键返回主菜单...")

        except KeyboardInterrupt:
            print("\n\n👋 再见!")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            input("按回车键继续...")

if __name__ == "__main__":
    main()
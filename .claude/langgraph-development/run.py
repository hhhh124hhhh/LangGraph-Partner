#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph学习环境 - 简化启动器
解决Windows编码问题的兼容版本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    print("=" * 60)
    print("LangGraph学习环境启动器")
    print("=" * 60)
    print()

    print("可用选项:")
    print("1. 快速环境配置")
    print("2. 运行演示示例")
    print("3. 启动Jupyter Lab")
    print("4. 交互式教程")
    print("5. 查看项目文档")
    print("q. 退出")
    print()

    choice = input("请选择 (1-5, q): ").strip()

    if choice == "q":
        print("再见!")
        return
    elif choice == "1":
        run_script("quick_start.py")
    elif choice == "2":
        run_script("demo_runner.py")
    elif choice == "3":
        start_jupyter()
    elif choice == "4":
        run_script("interactive_tutorial.py")
    elif choice == "5":
        show_docs()
    else:
        print("无效选择")

def run_script(script_name):
    """运行指定脚本"""
    script_path = Path("scripts") / script_name
    if script_path.exists():
        print(f"运行: {script_name}")
        try:
            subprocess.run([sys.executable, str(script_path)], check=False)
        except Exception as e:
            print(f"运行失败: {e}")
    else:
        print(f"脚本不存在: {script_path}")

def start_jupyter():
    """启动Jupyter Lab"""
    print("启动Jupyter Lab...")
    try:
        notebooks_dir = Path("notebooks")
        notebooks_dir.mkdir(exist_ok=True)

        subprocess.Popen([
            sys.executable, "-m", "jupyter", "lab",
            str(notebooks_dir), "--browser", "new"
        ])
        print("Jupyter Lab已启动!")
        print("访问: http://localhost:8888")
    except Exception as e:
        print(f"启动失败: {e}")
        print("请安装: pip install jupyter jupyterlab")

def show_docs():
    """显示文档信息"""
    docs = [
        ("新手指南", "docs/beginner_guide.md"),
        ("API参考", "references/api_reference.md"),
        ("架构模式", "references/architecture_patterns.md"),
    ]

    print("可用文档:")
    for name, path in docs:
        full_path = Path(path)
        if full_path.exists():
            print(f"[OK] {name}: {path}")
        else:
            print(f"[MISSING] {name}: {path}")

    print(f"\n项目根目录: {Path().absolute()}")
    print("\n提示: 运行 python start.py 获取完整功能")

if __name__ == "__main__":
    main()
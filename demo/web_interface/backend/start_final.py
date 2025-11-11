#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终后端启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """最终启动函数"""
    print("AI Partner Demo 后端启动 (最终版)")
    print("=" * 40)

    # 获取正确的路径
    script_dir = Path(__file__).parent
    demo_dir = script_dir.parent
    project_root = demo_dir.parent

    print(f"脚本目录: {script_dir}")
    print(f"项目根目录: {project_root}")

    # 查找venv
    venv_paths = [
        project_root / "venv",
        project_root.parent / "venv"  # 如果项目在其他位置
    ]

    venv_python = None
    for venv_path in venv_paths:
        venv_python = venv_path / "Scripts" / "python.exe"
        if venv_python.exists():
            print(f"找到虚拟环境: {venv_python}")
            break

    if not venv_python:
        print("ERROR: 未找到虚拟环境")
        return False

    # 设置Python路径
    os.environ["PYTHONPATH"] = str(project_root)

    print("环境变量已设置")

    # 测试导入AI Partner
    try:
        sys.path.insert(0, str(project_root))
        from agents.partner_agent import AIPartnerAgent
        print("SUCCESS: AI Partner导入成功")
    except Exception as e:
        print(f"WARNING: AI Partner导入失败: {e}")
        print("继续启动...")

    # 创建必要目录
    for dir_name in ["vector_db", "memory", "config", "logs"]:
        Path(dir_name).mkdir(exist_ok=True)

    print("目录创建完成")

    # 启动服务
    print("启动FastAPI服务...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 40)

    try:
        os.chdir(script_dir)

        # 检查app.main文件是否存在
        app_main = script_dir / "app" / "main.py"
        if not app_main.exists():
            print(f"ERROR: 未找到主应用文件: {app_main}")
            return False

        # 启动uvicorn
        subprocess.run([
            str(venv_python), "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        return False

    return True

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            input("按回车键退出...")
    except Exception as e:
        print(f"脚本执行失败: {e}")
        input("按回车键退出...")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化后端启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """简化启动函数"""
    print("AI Partner Demo 后端启动")
    print("=" * 40)

    # 检查虚拟环境
    current_dir = Path(__file__).parent
    demo_dir = current_dir.parent
    # venv在项目根目录，不是demo目录下
    project_root = demo_dir.parent
    venv_python = project_root / "venv" / "Scripts" / "python.exe"

    print(f"当前目录: {current_dir}")
    print(f"项目根目录: {project_root}")
    print(f"虚拟环境路径: {venv_python}")

    if not venv_python.exists():
        print("ERROR: 虚拟环境不存在")
        print(f"请创建: {project_root}/venv")
        return False

    # 设置项目路径
    langgraph_path = str(project_root)
    demo_path = str(current_dir)

    print(f"项目路径: {langgraph_path}")
    print(f"后端路径: {demo_path}")

    # 添加到Python路径
    sys.path.insert(0, langgraph_path)
    sys.path.insert(0, demo_path)

    print("Python路径已设置")

    # 检查环境配置
    env_file = Path(demo_path) / ".env"
    if not env_file.exists():
        print("ERROR: .env文件不存在")
        return False

    # 设置环境变量
    os.environ["PYTHONPATH"] = f"{langgraph_path};{demo_path}"
    print("环境变量已设置")

    # 测试导入
    try:
        print("测试导入AI Partner...")
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

    # 启动uvicorn
    print("启动FastAPI服务...")
    print("服务地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("按 Ctrl+C 停止服务")
    print("-" * 40)

    try:
        os.chdir(demo_path)
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
        main()
    except Exception as e:
        print(f"脚本执行失败: {e}")
        input("按回车键退出...")
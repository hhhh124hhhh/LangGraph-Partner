#!/usr/bin/env python3
"""
AI Partner API 启动脚本
提供便捷的开发和生产环境启动选项
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path


def setup_environment():
    """设置环境变量"""
    # 检查.env文件是否存在
    env_file = Path(".env")
    if not env_file.exists():
        print("ERROR: .env文件不存在，请从.env.example复制并配置")
        return False

    # 检查必要的环境变量
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"ERROR: 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请在.env文件中设置这些变量")
        return False

    return True


def install_dependencies():
    """安装依赖"""
    print("📦 安装Python依赖...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False


def create_directories():
    """创建必要的目录"""
    directories = ["vector_db", "memory", "config", "logs"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    print("✅ 目录结构创建完成")


def run_development():
    """运行开发环境"""
    print("🚀 启动开发环境...")

    # 设置开发环境变量
    os.environ["API_DEBUG"] = "true"
    os.environ["API_RELOAD"] = "true"

    try:
        subprocess.check_call([
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")


def run_production():
    """运行生产环境"""
    print("🚀 启动生产环境...")

    try:
        # 检查gunicorn是否安装
        subprocess.check_call([
            sys.executable, "-c", "import gunicorn"
        ])
    except subprocess.CalledProcessError:
        print("❌ 未安装gunicorn，正在安装...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "gunicorn"
        ])

    try:
        subprocess.check_call([
            "gunicorn",
            "app.main:app",
            "-w", "4",
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", "0.0.0.0:8000",
            "--log-level", "info",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--timeout", "120"
        ])
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")


def run_tests():
    """运行测试"""
    print("🧪 运行测试...")

    try:
        # 检查pytest是否安装
        subprocess.check_call([
            sys.executable, "-c", "import pytest"
        ])
    except subprocess.CalledProcessError:
        print("❌ 未安装pytest，正在安装...")
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "pytest pytest-asyncio pytest-cov"
        ])

    try:
        subprocess.check_call([
            sys.executable, "-m", "pytest",
            "tests/",
            "-v",
            "--cov=app",
            "--cov-report=term-missing"
        ])
    except subprocess.CalledProcessError as e:
        print(f"❌ 测试失败: {e}")


def check_health():
    """检查服务健康状态"""
    print("🔍 检查服务健康状态...")

    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)

        if response.status_code == 200:
            print("✅ 服务运行正常")
            print(f"📊 响应: {response.json()}")
        else:
            print(f"⚠️ 服务响应异常: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Partner API 启动脚本")
    parser.add_argument(
        "command",
        choices=["dev", "prod", "install", "test", "health", "setup"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="跳过依赖安装"
    )

    args = parser.parse_args()

    # 创建必要的目录
    create_directories()

    if args.command == "setup":
        print("🔧 初始化项目...")
        if setup_environment():
            if not args.skip_install:
                install_dependencies()
            print("✅ 项目初始化完成")
        else:
            sys.exit(1)

    elif args.command == "install":
        install_dependencies()

    elif args.command == "dev":
        if not setup_environment():
            sys.exit(1)
        run_development()

    elif args.command == "prod":
        if not setup_environment():
            sys.exit(1)
        run_production()

    elif args.command == "test":
        run_tests()

    elif args.command == "health":
        check_health()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
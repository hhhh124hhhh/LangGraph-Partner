#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LangGraph环境配置脚本

此脚本用于配置LangGraph开发环境，包括依赖安装、配置设置和环境验证。
"""

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """检查Python版本是否满足要求"""
    if sys.version_info < (3, 8):
        print("[ERROR] 需要Python 3.8或更高版本")
        return False
    print(f"[INFO] Python版本检查通过: {sys.version}")
    return True


def install_requirements():
    """安装必要的依赖包"""
    requirements = [
        "langgraph>=0.2.0",
        "langchain>=0.3.0",
        "langchain-core>=0.3.0",
        "langchain-openai>=0.2.0",
        "langchain-anthropic>=0.2.0",
        "langchain-community>=0.3.0",
        "langsmith>=0.1.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.0.0",
        "asyncio",
        "aiohttp>=3.8.0"
    ]

    print("[INFO] 安装LangGraph核心依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
        print("[SUCCESS] 核心依赖安装成功")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] 依赖安装失败: {e}")
        return False

    return True


def setup_optional_dependencies():
    """安装可选依赖"""
    optional_deps = {
        "database": ["redis>=5.0.0", "psycopg2-binary>=2.9.0", "sqlalchemy>=2.0.0"],
        "monitoring": ["prometheus-client>=0.19.0", "structlog>=23.0.0"],
        "testing": ["pytest>=7.0.0", "pytest-asyncio>=0.21.0", "pytest-mock>=3.10.0"],
        "development": ["black>=23.0.0", "isort>=5.12.0", "mypy>=1.5.0"]
    }

    print("[INFO] 安装可选依赖...")
    for category, deps in optional_deps.items():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + deps)
            print(f"[SUCCESS] {category}依赖安装成功")
        except subprocess.CalledProcessError as e:
            print(f"[WARNING] {category}依赖安装失败: {e}")


def create_env_file():
    """创建环境变量配置文件"""
    env_content = """# LangGraph配置
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=my-langgraph-app

# OpenAI API配置
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic API配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangSmith配置
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here

# 可选：数据库配置
# REDIS_URL=redis://localhost:6379/0
# POSTGRES_URL=postgresql://user:password@localhost/langgraph

# 可选：监控配置
# PROMETHEUS_PORT=8000
"""

    env_file = Path(".env")
    if not env_file.exists():
        env_file.write_text(env_content, encoding='utf-8')
        print("[SUCCESS] .env文件创建成功")
        print("[INFO] 请编辑.env文件，填入您的API密钥")
    else:
        print("[INFO] .env文件已存在，跳过创建")


def create_project_structure():
    """创建标准的项目结构"""
    directories = [
        "src",
        "src/agents",
        "src/tools",
        "src/stores",
        "src/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "config",
        "data",
        "logs",
        "notebooks"
    ]

    print("[INFO] 创建项目目录结构...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[INFO] 创建目录: {directory}")


def create_gitignore():
    """创建.gitignore文件"""
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Data
data/
*.db
*.sqlite

# LangGraph specific
langgraph_checkpoints/
langgraph_artifacts/

# OS
.DS_Store
Thumbs.db
"""

    gitignore_file = Path(".gitignore")
    if not gitignore_file.exists():
        gitignore_file.write_text(gitignore_content, encoding='utf-8')
        print("[SUCCESS] .gitignore文件创建成功")


def verify_installation():
    """验证安装是否成功"""
    print("[INFO] 验证LangGraph安装...")

    try:
        import langgraph
        print(f"[SUCCESS] LangGraph版本: {langgraph.__version__}")
    except ImportError:
        print("[ERROR] LangGraph导入失败")
        return False

    try:
        import langchain
        print(f"[SUCCESS] LangChain版本: {langchain.__version__}")
    except ImportError:
        print("[ERROR] LangChain导入失败")
        return False

    return True


def main():
    """主函数"""
    print("=" * 60)
    print("LangGraph环境配置脚本")
    print("=" * 60)

    # 检查Python版本
    if not check_python_version():
        sys.exit(1)

    # 安装依赖
    if not install_requirements():
        print("[ERROR] 核心依赖安装失败，请检查网络连接和pip配置")
        sys.exit(1)

    # 安装可选依赖
    setup_optional_dependencies()

    # 创建项目结构
    create_project_structure()

    # 创建配置文件
    create_env_file()
    create_gitignore()

    # 验证安装
    if verify_installation():
        print("\n" + "=" * 60)
        print("[SUCCESS] LangGraph环境配置完成！")
        print("=" * 60)
        print("\n下一步:")
        print("1. 编辑.env文件，添加您的API密钥")
        print("2. 运行 'python scripts/generate_template.py' 创建项目模板")
        print("3. 参考 'references/' 目录中的文档进行开发")
    else:
        print("\n[ERROR] 环境配置失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
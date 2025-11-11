#!/usr/bin/env python3
"""
AI Partner Demo 环境检查脚本
检查是否具备启动Demo的所有条件
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python版本过低: {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)")
        return False

def check_virtual_environment():
    """检查虚拟环境"""
    print("📦 检查虚拟环境...")

    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"

    if not venv_path.exists():
        print("❌ 未找到虚拟环境")
        print(f"请在项目根目录创建: {project_root}")
        print("python -m venv venv")
        return False

    # 检查虚拟环境中是否有Python
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    if python_path.exists():
        print(f"✅ 虚拟环境: {venv_path}")
        return True
    else:
        print("❌ 虚拟环境中未找到Python")
        return False

def check_nodejs():
    """检查Node.js"""
    print("📦 检查Node.js...")
    try:
        result = subprocess.run(["node", "--version"],
                              check=True, capture_output=True, text=True)
        print(f"✅ Node.js {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ 未找到Node.js")
        print("请安装: https://nodejs.org/")
        return False

def check_ai_partner_dependencies():
    """检查AI Partner依赖"""
    print("🤖 检查AI Partner依赖...")

    try:
        # 检查是否可以导入LangGraph
        import langgraph
        print(f"✅ LangGraph {langgraph.__version__}")

        # 检查是否可以导入ChromaDB
        import chromadb
        print(f"✅ ChromaDB {chromadb.__version__}")

        # 检查智能体文件
        project_root = Path(__file__).parent.parent
        agent_file = project_root / "agents" / "partner_agent.py"

        if agent_file.exists():
            print("✅ AI Partner智能体文件存在")

            # 尝试导入
            sys.path.append(str(project_root))
            try:
                from agents.partner_agent import AIPartnerAgent
                print("✅ AI Partner智能体可导入")
                return True
            except Exception as e:
                print(f"⚠️  AI Partner智能体导入警告: {e}")
                return True  # 继续尝试
        else:
            print("❌ 未找到AI Partner智能体文件")
            return False

    except ImportError as e:
        print(f"❌ 缺少必要依赖: {e}")
        print("请在虚拟环境中安装依赖:")
        print("pip install langgraph chromadb")
        return False

def check_demo_files():
    """检查Demo文件"""
    print("📁 检查Demo文件...")

    demo_dir = Path(__file__).parent

    required_files = [
        "web_interface/backend/app/main.py",
        "web_interface/frontend/package.json",
        "demo_data/personas/demo_personas.json",
        ".env.example"
    ]

    all_exist = True
    for file_path in required_files:
        full_path = demo_dir / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ 缺少文件: {file_path}")
            all_exist = False

    return all_exist

def check_ports():
    """检查端口占用"""
    print("🔌 检查端口占用...")

    import socket

    def is_port_occupied(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    ports = [(8000, "后端API"), (3000, "前端界面")]

    all_available = True
    for port, service in ports:
        if is_port_occupied(port):
            print(f"⚠️  端口 {port} ({service}) 已被占用")
            all_available = False
        else:
            print(f"✅ 端口 {port} ({service}) 可用")

    return all_available

def check_api_key():
    """检查API密钥配置"""
    print("🔑 检查API密钥配置...")

    demo_dir = Path(__file__).parent
    env_file = demo_dir / "web_interface" / "backend" / ".env"

    if env_file.exists():
        with open(env_file, 'r') as f:
            content = f.read()
            if 'your_zhipu_api_key_here' in content:
                print("⚠️  请设置智谱AI API密钥")
                print(f"编辑文件: {env_file}")
                return False
            elif 'ZHIPU_API_KEY=' in content:
                print("✅ API密钥已配置")
                return True

    print("⚠️  未找到环境配置文件")
    print(f"请创建: {env_file}")
    return False

def main():
    """主检查函数"""
    print("AI Partner Demo 环境检查")
    print("=" * 50)

    checks = [
        ("Python版本", check_python_version),
        ("虚拟环境", check_virtual_environment),
        ("Node.js", check_nodejs),
        ("AI Partner依赖", check_ai_partner_dependencies),
        ("Demo文件", check_demo_files),
        ("端口可用性", check_ports),
        ("API密钥", check_api_key)
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} 检查出错: {e}")
            results.append((name, False))

    print("\n" + "=" * 50)
    print("📊 检查结果汇总:")

    success_count = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<15} {status}")
        if result:
            success_count += 1

    print(f"\n总体状态: {success_count}/{len(results)} 项检查通过")

    if success_count == len(results):
        print("\n🎉 环境检查完成！可以启动Demo了！")
        print("\n启动命令:")
        print("cd demo && python start_demo_simplified.py")
    else:
        print("\n⚠️  请解决上述问题后再启动Demo")
        print("参考文档: QUICK_START_SIMPLIFIED.md")

    return success_count == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
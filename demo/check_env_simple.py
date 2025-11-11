#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Partner Demo 简化环境检查脚本
避免emoji编码问题
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    """打印标题"""
    print("=" * 60)
    print("AI Partner Demo 环境检查")
    print("=" * 60)

def check_python_version():
    """检查Python版本"""
    print("[1] 检查Python版本...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"    OK: Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"    FAIL: Python版本过低 {version.major}.{version.minor}.{version.micro} (需要 >= 3.8)")
        return False

def check_virtual_environment():
    """检查虚拟环境"""
    print("[2] 检查虚拟环境...")

    project_root = Path(__file__).parent.parent
    venv_path = project_root / "venv"

    if not venv_path.exists():
        print("    FAIL: 未找到虚拟环境")
        print(f"    请在项目根目录创建: {project_root}")
        return False

    # 检查虚拟环境中是否有Python
    if os.name == 'nt':  # Windows
        python_path = venv_path / "Scripts" / "python.exe"
    else:
        python_path = venv_path / "bin" / "python"

    if python_path.exists():
        print(f"    OK: 虚拟环境存在 {venv_path}")
        return True
    else:
        print("    FAIL: 虚拟环境中未找到Python")
        return False

def check_nodejs():
    """检查Node.js"""
    print("[3] 检查Node.js...")
    try:
        result = subprocess.run(["node", "--version"],
                              check=True, capture_output=True, text=True)
        print(f"    OK: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("    FAIL: 未找到Node.js")
        print("    请安装: https://nodejs.org/")
        return False

def check_ai_partner_dependencies():
    """检查AI Partner依赖"""
    print("[4] 检查AI Partner依赖...")

    try:
        # 检查是否可以导入LangGraph
        import langgraph
        print(f"    OK: LangGraph {langgraph.__version__}")

        # 检查智能体文件
        project_root = Path(__file__).parent.parent
        agent_file = project_root / "agents" / "partner_agent.py"

        if agent_file.exists():
            print("    OK: AI Partner智能体文件存在")
            return True
        else:
            print("    FAIL: 未找到AI Partner智能体文件")
            return False

    except ImportError as e:
        print(f"    FAIL: 缺少必要依赖: {e}")
        print("    请在虚拟环境中安装依赖")
        return False

def check_demo_files():
    """检查Demo文件"""
    print("[5] 检查Demo文件...")

    demo_dir = Path(__file__).parent

    required_files = [
        "web_interface/backend/app/main.py",
        "web_interface/frontend/package.json",
        "demo_data/personas/demo_personas.json"
    ]

    all_exist = True
    for file_path in required_files:
        full_path = demo_dir / file_path
        if full_path.exists():
            print(f"    OK: {file_path}")
        else:
            print(f"    FAIL: 缺少文件 {file_path}")
            all_exist = False

    return all_exist

def check_ports():
    """检查端口占用"""
    print("[6] 检查端口可用性...")

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
            print(f"    WARNING: 端口 {port} ({service}) 已被占用")
        else:
            print(f"    OK: 端口 {port} ({service}) 可用")

    return all_available

def check_api_key_config():
    """检查API密钥配置"""
    print("[7] 检查API密钥配置...")

    demo_dir = Path(__file__).parent
    env_example = demo_dir / "web_interface" / "backend" / ".env.example"
    env_file = demo_dir / "web_interface" / "backend" / ".env"

    if not env_example.exists():
        print(f"    WARNING: 未找到环境示例文件 {env_example}")
        return False

    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'your_zhipu_api_key_here' in content:
                print(f"    WARNING: 请设置智谱AI API密钥")
                print(f"    编辑文件: {env_file}")
                return False
            elif 'ZHIPU_API_KEY=' in content and len(content) > 20:
                print("    OK: API密钥已配置")
                return True

    print(f"    INFO: 创建环境配置文件 {env_file}")
    try:
        import shutil
        shutil.copy(env_example, env_file)
        print("    OK: 已创建.env文件，请设置API密钥")
        return True
    except Exception as e:
        print(f"    FAIL: 无法创建配置文件: {e}")
        return False

def print_summary(results):
    """打印检查结果汇总"""
    print("\n" + "=" * 60)
    print("检查结果汇总:")
    print("=" * 60)

    success_count = 0
    for name, result in results:
        status = "通过" if result else "失败"
        print(f"{name:<20} {status}")
        if result:
            success_count += 1

    print(f"\n总体状态: {success_count}/{len(results)} 项检查通过")

    if success_count >= len(results) - 1:  # 允许一个警告
        print("\n[SUCCESS] 环境检查完成！可以启动Demo了！")
        print("\n启动命令:")
        print("1. 激活虚拟环境:")
        print("   cd ../ && ./venv/Scripts/activate")
        print("2. 启动Demo:")
        print("   cd demo && python start_demo_simplified.py")
        return True
    else:
        print("\n[ERROR] 请解决上述问题后再启动Demo")
        print("参考文档: QUICK_START_SIMPLIFIED.md")
        return False

def main():
    """主检查函数"""
    try:
        print_header()

        checks = [
            ("Python版本", check_python_version),
            ("虚拟环境", check_virtual_environment),
            ("Node.js", check_nodejs),
            ("AI Partner依赖", check_ai_partner_dependencies),
            ("Demo文件", check_demo_files),
            ("端口可用性", check_ports),
            ("API密钥配置", check_api_key_config)
        ]

        results = []
        for name, check_func in checks:
            try:
                result = check_func()
                results.append((name, result))
            except Exception as e:
                print(f"    ERROR: {name} 检查出错: {e}")
                results.append((name, False))

        return print_summary(results)

    except Exception as e:
        print(f"环境检查脚本出错: {e}")
        return False

if __name__ == "__main__":
    success = main()
    input("\n按回车键退出...")
    sys.exit(0 if success else 1)
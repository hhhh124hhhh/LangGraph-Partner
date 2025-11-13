#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Partner 统一后端启动脚本
功能：
1. 自动加载 demo 根目录的环境变量
2. 设置正确的项目路径和Python路径
3. 提供开发/生产环境启动选项
4. 自动安装依赖（可选）
5. 检查服务健康状态
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path

def get_paths():
    """获取正确的文件路径"""
    script_dir = Path(__file__).parent
    backend_dir = script_dir
    frontend_dir = script_dir.parent / "frontend"
    demo_dir = script_dir.parent.parent  # demo根目录
    project_root = demo_dir.parent  # LangGraph根目录
    
    return {
        "script_dir": script_dir,
        "backend_dir": backend_dir,
        "frontend_dir": frontend_dir,
        "demo_dir": demo_dir,
        "project_root": project_root
    }

def get_virtual_env_path(paths):
    """获取虚拟环境路径
    检查以下位置:
    1. 项目根目录下的.venv
    2. demo目录下的.venv
    3. backend目录下的.venv
    """
    possible_venv_paths = [
        paths['project_root'] / ".venv",
        paths['demo_dir'] / ".venv",
        paths['backend_dir'] / ".venv"
    ]
    
    # 检查是否存在已有的虚拟环境
    for venv_path in possible_venv_paths:
        if venv_path.exists():
            print(f"✅ 找到已存在的虚拟环境: {venv_path}")
            return venv_path
    
    # 默认在demo目录下创建虚拟环境
    default_venv_path = paths['demo_dir'] / ".venv"
    print(f"⚠️ 未找到虚拟环境，将在: {default_venv_path} 创建新的虚拟环境")
    return default_venv_path

def get_venv_python(venv_path):
    """获取虚拟环境中的Python解释器路径"""
    if sys.platform == "win32":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"

def create_virtual_environment(venv_path):
    """创建虚拟环境"""
    if venv_path.exists():
        print(f"✅ 虚拟环境已存在: {venv_path}")
        return True
    
    print(f"📦 创建虚拟环境: {venv_path}")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        print("✅ 虚拟环境创建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 虚拟环境创建失败: {e}")
        return False

def setup_environment(paths, force_reload=False):
    """设置环境变量"""
    print("AI Partner Demo 后端启动")
    print("=" * 40)
    print(f"脚本目录: {paths['script_dir']}")
    print(f"后端目录: {paths['backend_dir']}")
    print(f"Demo根目录: {paths['demo_dir']}")
    print(f"项目根目录: {paths['project_root']}")
    
    # 设置Python路径
    if not force_reload and os.getenv("PYTHONPATH"):
        print(f"Python路径已设置: {os.getenv('PYTHONPATH')}")
    else:
        os.environ["PYTHONPATH"] = str(paths['project_root'])
        print(f"设置Python路径: {os.environ['PYTHONPATH']}")
    
    # 加载环境变量文件
    env_path = paths['demo_dir'] / ".env"
    if not env_path.exists():
        print(f"ERROR: 未找到环境变量文件: {env_path}")
        return False
    
    print(f"加载环境变量文件: {env_path}")
    
    # 尝试使用dotenv加载环境变量
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=force_reload)
    except ImportError:
        print("dotenv模块未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-dotenv"])
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=env_path, override=force_reload)
    
    # 打印关键环境变量
    print("\n环境变量加载状态:")
    key_vars = ["OPENAI_API_KEY", "DEFAULT_MODEL", "DEMO_MODE", "ENVIRONMENT"]
    for var in key_vars:
        value = os.getenv(var)
        if var == "OPENAI_API_KEY" and value:
            value = f"{value[:8]}...{value[-8:]}"  # 隐藏部分API密钥
        print(f"{var}: {value or '未设置'}")
    
    return True

def install_dependencies(paths, venv_python):
    """安装依赖"""
    print("\n📦 安装Python依赖...")
    
    # 检查requirements.txt是否存在
    req_files = [
        paths['backend_dir'] / "requirements.txt",
        paths['backend_dir'] / "requirements_simplified.txt"
    ]
    
    req_file = None
    for f in req_files:
        if f.exists():
            req_file = f
            break
    
    if not req_file:
        print("ERROR: 未找到requirements.txt文件")
        return False
    
    try:
        subprocess.check_call([
            str(venv_python), "-m", "pip", "install", "--upgrade", "pip"
        ])
        subprocess.check_call([
            str(venv_python), "-m", "pip", "install", "-r", str(req_file)
        ])
        print("✅ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 依赖安装失败: {e}")
        return False

def create_directories(paths):
    """创建必要的目录"""
    print("\n📁 创建必要目录...")
    
    # 相对于backend目录的目录结构
    directories = ["vector_db", "memory", "config", "logs"]
    
    for directory in directories:
        dir_path = paths['backend_dir'] / directory
        dir_path.mkdir(exist_ok=True)
        print(f"✅ 创建目录: {dir_path}")

def test_ai_partner_import(paths, venv_python):
    """测试AI Partner导入"""
    print("\n🔍 测试AI Partner导入...")
    
    try:
        # 使用虚拟环境中的Python执行导入测试
        test_script = f"""
import sys
sys.path.insert(0, '{paths['project_root']}')
from agents.partner_agent import AIPartnerAgent
print('SUCCESS')
"""
        
        result = subprocess.run([str(venv_python), "-c", test_script], 
                               capture_output=True, text=True)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print("✅ AI Partner导入成功")
            return True
        else:
            error_msg = result.stderr.strip() or "未知错误"
            print(f"⚠️ AI Partner导入失败: {error_msg}")
            print("继续启动服务，但某些功能可能受限")
            return False
            
    except Exception as e:
        print(f"⚠️ AI Partner导入失败: {e}")
        print("继续启动服务，但某些功能可能受限")
        return False

def run_development(paths, venv_python):
    """运行开发环境"""
    print("\n🚀 启动开发环境...")
    
    # 设置开发环境变量
    os.environ["API_DEBUG"] = "true"
    os.environ["API_RELOAD"] = "true"
    
    # 检查主应用文件
    app_main = paths['backend_dir'] / "app" / "main.py"
    if not app_main.exists():
        print(f"ERROR: 未找到主应用文件: {app_main}")
        return False
    
    try:
        # 进入backend目录
        os.chdir(paths['backend_dir'])
        
        # 启动uvicorn
        subprocess.run([
            str(venv_python), "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--log-level", "info"
        ])
        return True
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动过程中发生错误: {e}")
        return False

def run_production(paths, venv_python):
    """运行生产环境"""
    print("\n🚀 启动生产环境...")
    
    # 检查主应用文件
    app_main = paths['backend_dir'] / "app" / "main.py"
    if not app_main.exists():
        print(f"ERROR: 未找到主应用文件: {app_main}")
        return False
    
    try:
        # 检查gunicorn是否安装
        try:
            subprocess.check_call([str(venv_python), "-c", "import gunicorn"])
        except subprocess.CalledProcessError:
            print("安装gunicorn...")
            subprocess.check_call([str(venv_python), "-m", "pip", "install", "gunicorn"])
        
        # 获取gunicorn路径
        gunicorn_path = str(venv_python.parent / ("Scripts\gunicorn.exe" if sys.platform == "win32" else "bin/gunicorn"))
        
        # 进入backend目录
        os.chdir(paths['backend_dir'])
        
        # 启动gunicorn
        subprocess.run([
            gunicorn_path,
            "app.main:app",
            "-w", "4",
            "-k", "uvicorn.workers.UvicornWorker",
            "--bind", "0.0.0.0:8000",
            "--log-level", "info",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "--timeout", "120"
        ])
        return True
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 服务启动失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 启动过程中发生错误: {e}")
        return False

def check_health():
    """检查服务健康状态"""
    print("\n🔍 检查服务健康状态...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ 服务运行正常")
            print(f"📊 响应: {response.json()}")
        else:
            print(f"⚠️ 服务响应异常: {response.status_code}")
            print(f"响应内容: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务，请检查服务是否已启动")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="AI Partner 统一后端启动脚本")
    parser.add_argument(
        "command",
        choices=["dev", "prod", "install", "health", "setup"],
        help="要执行的命令"
    )
    parser.add_argument(
        "--skip-install",
        action="store_true",
        help="跳过依赖安装"
    )
    parser.add_argument(
        "--force-reload",
        action="store_true",
        help="强制重新加载环境变量"
    )
    parser.add_argument(
        "--venv-path",
        type=str,
        help="指定虚拟环境路径（可选）"
    )
    
    args = parser.parse_args()
    
    # 获取路径信息
    paths = get_paths()
    
    # 虚拟环境管理
    if args.venv_path:
        venv_path = Path(args.venv_path)
    else:
        venv_path = get_virtual_env_path(paths)
    
    # 创建虚拟环境（如果不存在）
    if not create_virtual_environment(venv_path):
        sys.exit(1)
    
    # 获取虚拟环境中的Python解释器
    venv_python = get_venv_python(venv_path)
    if not venv_python.exists():
        print(f"❌ 虚拟环境Python解释器不存在: {venv_python}")
        sys.exit(1)
    
    print(f"📌 使用虚拟环境Python: {venv_python}")
    
    if args.command == "setup":
        """初始化项目"""
        print("🔧 初始化项目...")
        
        # 创建必要目录
        create_directories(paths)
        
        # 加载环境变量
        if not setup_environment(paths, args.force_reload):
            sys.exit(1)
        
        # 安装依赖
        if not args.skip_install:
            if not install_dependencies(paths, venv_python):
                sys.exit(1)
        
        # 测试AI Partner导入
        test_ai_partner_import(paths, venv_python)
        
        print("\n✅ 项目初始化完成！")
        print("使用以下命令启动服务:")
        print(f"  {sys.executable} start_ai_partner.py dev")
        
    elif args.command == "install":
        """仅安装依赖"""
        install_dependencies(paths, venv_python)
        
    elif args.command == "dev":
        """开发环境启动"""
        # 创建必要目录
        create_directories(paths)
        
        # 加载环境变量
        if not setup_environment(paths, args.force_reload):
            sys.exit(1)
        
        # 安装依赖（如果需要）
        if not args.skip_install:
            install_dependencies(paths, venv_python)
        
        # 测试AI Partner导入
        test_ai_partner_import(paths, venv_python)
        
        # 启动开发服务器
        run_development(paths, venv_python)
        
    elif args.command == "prod":
        """生产环境启动"""
        # 创建必要目录
        create_directories(paths)
        
        # 加载环境变量
        if not setup_environment(paths, args.force_reload):
            sys.exit(1)
        
        # 安装依赖（如果需要）
        if not args.skip_install:
            install_dependencies(paths, venv_python)
        
        # 测试AI Partner导入
        test_ai_partner_import(paths, venv_python)
        
        # 启动生产服务器
        run_production(paths, venv_python)
        
    elif args.command == "health":
        """检查服务健康状态"""
        check_health()
        
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 脚本已中断")
    except Exception as e:
        print(f"\n❌ 脚本执行失败: {e}")
        input("按回车键退出...")
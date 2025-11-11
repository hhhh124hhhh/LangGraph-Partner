#!/usr/bin/env python3
"""
AI Partner Demo 简化启动脚本
复用现有虚拟环境，快速启动演示系统
"""

import os
import sys
import time
import signal
import subprocess
import threading
import webbrowser
from pathlib import Path

class SimplifiedDemoLauncher:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "web_interface" / "backend"
        self.frontend_dir = self.demo_dir / "web_interface" / "frontend"
        self.project_root = self.demo_dir.parent
        self.processes = []
        self.original_dir = Path.cwd()

    def print_banner(self):
        """打印启动横幅"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                AI Partner 智能体演示系统                      ║
║                                                              ║
║    🤖 基于 LangGraph 的个性化AI对话伙伴                        ║
║    🧠 智能记忆管理 + 向量化知识检索                            ║
║    🎯 从Coze到LangGraph的技术升级展示                          ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(banner)

    def check_virtual_environment(self):
        """检查虚拟环境"""
        print("🔍 检查虚拟环境...")

        venv_path = self.project_root / "venv"

        if not venv_path.exists():
            print("❌ 错误: 未找到虚拟环境")
            print(f"请在项目根目录创建虚拟环境:")
            print(f"cd {self.project_root}")
            print(f"python -m venv venv")
            return False

        # 检查虚拟环境中是否有必要的包
        if os.name == 'nt':  # Windows
            python_path = venv_path / "Scripts" / "python.exe"
            pip_path = venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Mac
            python_path = venv_path / "bin" / "python"
            pip_path = venv_path / "bin" / "pip"

        if not python_path.exists():
            print("❌ 错误: 虚拟环境中未找到Python")
            return False

        print("✅ 虚拟环境检查完成")
        self.python_path = python_path
        return True

    def check_frontend_requirements(self):
        """检查前端要求"""
        print("🔍 检查前端环境...")

        # 检查Node.js
        try:
            result = subprocess.run(["node", "--version"],
                                  check=True, capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 错误: 请安装Node.js")
            print("下载地址: https://nodejs.org/")
            return False

        # 检查npm
        try:
            result = subprocess.run(["npm", "--version"],
                                  check=True, capture_output=True, text=True)
            print(f"✅ npm: {result.stdout.strip()}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 错误: 请安装npm")
            return False

        return True

    def install_backend_dependencies(self):
        """安装后端依赖"""
        print("📦 检查后端依赖...")

        requirements_file = self.backend_dir / "requirements.txt"
        if not requirements_file.exists():
            print("⚠️  后端依赖文件不存在，跳过安装")
            return True

        # 使用现有虚拟环境安装依赖
        try:
            print("正在安装后端依赖...")
            result = subprocess.run(
                [str(self.python_path), "-m", "pip", "install", "-r", str(requirements_file)],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ 后端依赖检查完成")
                return True
            else:
                print("⚠️  后端依赖安装可能有问题，但继续尝试启动...")
                print(result.stderr)
                return True

        except Exception as e:
            print(f"⚠️  依赖检查警告: {e}")
            return True  # 继续尝试启动

    def install_frontend_dependencies(self):
        """安装前端依赖"""
        print("📦 检查前端依赖...")

        os.chdir(self.frontend_dir)

        # 检查是否已安装依赖
        if (self.frontend_dir / "node_modules").exists():
            print("✅ 前端依赖已安装")
            return True

        try:
            print("正在安装前端依赖...")
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ 前端依赖安装完成")
                return True
            else:
                print(f"❌ 前端依赖安装失败: {result.stderr}")
                return False

        except Exception as e:
            print(f"❌ 前端依赖安装错误: {e}")
            return False

    def setup_environment(self):
        """设置环境"""
        print("⚙️  设置环境...")

        # 检查环境变量文件
        env_file = self.backend_dir / ".env"
        env_example = self.backend_dir / ".env.example"

        if not env_file.exists() and env_example.exists():
            print("📝 创建环境变量文件...")
            import shutil
            shutil.copy(env_example, env_file)
            print("⚠️  请编辑后端目录下的 .env 文件，设置您的API密钥")

        # 检查API密钥
        if env_file.exists():
            with open(env_file, 'r') as f:
                content = f.read()
                if 'your_zhipu_api_key_here' in content:
                    print("⚠️  警告: 请设置您的智谱AI API密钥!")
                    print(f"编辑文件: {env_file}")

        return True

    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")

        os.chdir(self.backend_dir)

        try:
            # 使用虚拟环境中的Python启动后端
            process = subprocess.Popen(
                [str(self.python_path), "run.py", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("backend", process))

            # 等待后端启动
            print("等待后端启动...")
            time.sleep(6)

            # 简单的健康检查
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex(('localhost', 8000))
                sock.close()

                if result == 0:
                    print("✅ 后端服务启动成功 (http://localhost:8000)")
                    return True
                else:
                    print("⚠️  后端服务可能还在启动中...")
                    return True

            except Exception as e:
                print(f"⚠️  健康检查失败，但服务可能正在启动: {e}")
                return True

        except Exception as e:
            print(f"❌ 后端启动失败: {e}")
            return False

    def start_frontend(self):
        """启动前端服务"""
        print("🚀 启动前端服务...")

        os.chdir(self.frontend_dir)

        try:
            process = subprocess.Popen(
                ["npm", "run", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("frontend", process))

            # 等待前端启动
            print("等待前端启动...")
            time.sleep(10)

            print("✅ 前端服务启动成功 (http://localhost:3000)")
            return True

        except Exception as e:
            print(f"❌ 前端启动失败: {e}")
            return False

    def open_browser(self):
        """打开浏览器"""
        print("🌐 打开浏览器...")
        try:
            webbrowser.open("http://localhost:3000")
            print("✅ 浏览器已打开演示页面")
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")
            print("请手动访问: http://localhost:3000")

    def monitor_services(self):
        """监控服务状态"""
        def monitor():
            while True:
                time.sleep(15)
                for name, process in self.processes:
                    if process.poll() is not None:
                        print(f"⚠️  {name} 服务意外停止")
                        return

        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()

    def cleanup(self):
        """清理资源"""
        print("\n🧹 清理资源...")
        for name, process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} 服务已停止")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"🔨 强制停止 {name} 服务")
            except Exception as e:
                print(f"⚠️  停止 {name} 服务时出错: {e}")

    def signal_handler(self, signum, frame):
        """信号处理器"""
        print(f"\n收到信号 {signum}, 正在关闭...")
        self.cleanup()
        sys.exit(0)

    def run(self):
        """运行演示系统"""
        self.print_banner()

        # 注册信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            # 检查虚拟环境
            if not self.check_virtual_environment():
                return False

            # 检查前端环境
            if not self.check_frontend_requirements():
                return False

            # 安装依赖
            if not self.install_backend_dependencies():
                return False

            if not self.install_frontend_dependencies():
                return False

            # 设置环境
            if not self.setup_environment():
                return False

            # 启动服务
            if not self.start_backend():
                return False

            if not self.start_frontend():
                return False

            # 监控服务
            self.monitor_services()

            # 打开浏览器
            self.open_browser()

            print("""
╔══════════════════════════════════════════════════════════════╗
║                    🎉 演示系统启动成功！                       ║
╠══════════════════════════════════════════════════════════════╣
║ 前端界面: http://localhost:3000                               ║
║ 后端API:  http://localhost:8000                               ║
║ API文档:  http://localhost:8000/docs                          ║
║                                                              ║
║ 复用现有虚拟环境，无需重复安装依赖！                           ║
║ 按 Ctrl+C 停止所有服务                                         ║
╚══════════════════════════════════════════════════════════════╝
            """)

            # 保持运行
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass

        except Exception as e:
            print(f"❌ 启动失败: {e}")
            return False
        finally:
            self.cleanup()

        return True

def main():
    """主函数"""
    launcher = SimplifiedDemoLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
AI Partner Demo 启动脚本
一键启动完整的演示系统
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
import webbrowser
import json

class DemoLauncher:
    def __init__(self):
        self.demo_dir = Path(__file__).parent
        self.backend_dir = self.demo_dir / "web_interface" / "backend"
        self.frontend_dir = self.demo_dir / "web_interface" / "frontend"
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

    def check_requirements(self):
        """检查系统要求"""
        print("🔍 检查系统要求...")

        # 检查Python版本
        if sys.version_info < (3, 8):
            print("❌ 错误: 需要Python 3.8或更高版本")
            return False

        # 检查Node.js
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            print("✅ Node.js 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 错误: 请安装Node.js")
            return False

        # 检查npm
        try:
            subprocess.run(["npm", "--version"], check=True, capture_output=True)
            print("✅ npm 已安装")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ 错误: 请安装npm")
            return False

        # 检查演示数据
        demo_data_dir = self.demo_dir / "demo_data"
        if not demo_data_dir.exists():
            print("❌ 错误: 演示数据目录不存在")
            return False

        print("✅ 系统要求检查完成")
        return True

    def setup_environment(self):
        """设置环境"""
        print("⚙️  设置环境...")

        # 设置后端环境
        os.chdir(self.backend_dir)

        # 创建虚拟环境（如果不存在）
        venv_dir = self.backend_dir / "venv"
        if not venv_dir.exists():
            print("📦 创建后端虚拟环境...")
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

        # 激活虚拟环境并安装依赖
        if os.name == 'nt':  # Windows
            pip_path = venv_dir / "Scripts" / "pip"
            python_path = venv_dir / "Scripts" / "python"
        else:  # Unix/Mac
            pip_path = venv_dir / "bin" / "pip"
            python_path = venv_dir / "bin" / "python"

        print("📦 安装后端依赖...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)

        # 设置前端环境
        os.chdir(self.frontend_dir)
        if not (self.frontend_dir / "node_modules").exists():
            print("📦 安装前端依赖...")
            subprocess.run(["npm", "install"], check=True)

        print("✅ 环境设置完成")
        return True

    def start_backend(self):
        """启动后端服务"""
        print("🚀 启动后端服务...")

        os.chdir(self.backend_dir)

        # 激活虚拟环境
        if os.name == 'nt':  # Windows
            python_path = self.backend_dir / "venv" / "Scripts" / "python"
        else:  # Unix/Mac
            python_path = self.backend_dir / "venv" / "bin" / "python"

        # 启动后端服务
        try:
            process = subprocess.Popen(
                [str(python_path), "run.py", "dev"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes.append(("backend", process))

            # 等待后端启动
            time.sleep(5)

            # 检查后端是否正常启动
            try:
                response = subprocess.run(
                    ["curl", "-f", "http://localhost:8000/health"],
                    capture_output=True,
                    timeout=5
                )
                if response.returncode == 0:
                    print("✅ 后端服务启动成功 (http://localhost:8000)")
                    return True
            except:
                pass

            print("⚠️  后端服务可能正在启动中...")
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
            time.sleep(8)

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
                time.sleep(10)
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
            # 检查系统要求
            if not self.check_requirements():
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
    launcher = DemoLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
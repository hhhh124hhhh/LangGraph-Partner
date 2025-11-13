#!/usr/bin/env python3
"""
配置验证脚本
验证前后端环境变量配置是否正确加载
"""

import os
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*50}")
    print(f" {title}")
    print('='*50)

def verify_backend_config():
    """验证后端配置加载"""
    print_section("后端配置验证")

    # 添加后端路径到 Python 路径
    backend_path = Path(__file__).parent / "web_interface" / "backend"
    sys.path.insert(0, str(backend_path))

    try:
        from app.core.config import settings

        print(f"[SUCCESS] 配置文件加载成功")
        print(f"[PATH] .env 路径: {Path(__file__).parent / '.env'}")

        # 检查关键配置项
        print(f"\n[SERVER] 服务器配置:")
        print(f"   - API_HOST: {settings.api_host}")
        print(f"   - API_PORT: {settings.api_port}")
        print(f"   - API_DEBUG: {settings.api_debug}")
        print(f"   - API_RELOAD: {settings.api_reload}")

        print(f"\n[AI] AI 模型配置:")
        print(f"   - LLM_MODEL: {settings.llm_model}")
        print(f"   - OPENAI_API_KEY: {'已设置' if settings.openai_api_key else '未设置'}")
        print(f"   - OPENAI_BASE_URL: {settings.openai_base_url}")

        print(f"\n[STORAGE] 存储路径:")
        print(f"   - VECTOR_DB_PATH: {settings.vector_db_path}")
        print(f"   - MEMORY_DIR: {settings.memory_dir}")
        print(f"   - CONFIG_DIR: {settings.config_dir}")

        print(f"\n[CORS] CORS 配置:")
        print(f"   - CORS_ORIGINS: {settings.cors_origins}")

        return True

    except Exception as e:
        print(f"[ERROR] 后端配置加载失败: {e}")
        return False

def verify_frontend_config():
    """验证前端环境变量"""
    print_section("前端配置验证")

    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print(f"[ERROR] 找不到 .env 文件: {env_path}")
        return False

    print(f"[SUCCESS] 找到 .env 文件: {env_path}")

    # 读取并解析 .env 文件
    frontend_vars = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.startswith('VITE_'):
                        frontend_vars[key] = value
    except Exception as e:
        print(f"[ERROR] 读取 .env 文件失败: {e}")
        return False

    print(f"\n[FRONTEND] 前端环境变量 (VITE_ 前缀):")

    # 关键前端配置项
    key_vars = [
        'VITE_API_BASE_URL',
        'VITE_WS_URL',
        'VITE_APP_NAME',
        'VITE_APP_VERSION',
        'VITE_ENVIRONMENT',
        'VITE_DEBUG',
        'VITE_DEFAULT_MODEL'
    ]

    for var in key_vars:
        value = frontend_vars.get(var, '未设置')
        print(f"   - {var}: {value}")

    print(f"\n[INFO] 总计找到 {len(frontend_vars)} 个前端环境变量")

    # 检查关键配置是否存在
    required_vars = ['VITE_API_BASE_URL', 'VITE_WS_URL']
    missing_vars = [var for var in required_vars if var not in frontend_vars]

    if missing_vars:
        print(f"[WARNING] 缺少关键配置: {missing_vars}")
        return False

    return True

def verify_port_consistency():
    """验证端口配置一致性"""
    print_section("端口配置一致性检查")

    env_path = Path(__file__).parent / ".env"

    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取端口配置
        backend_port = None
        frontend_api_host = None
        frontend_ws_host = None

        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('API_PORT='):
                backend_port = line.split('=', 1)[1]
            elif line.startswith('VITE_API_BASE_URL='):
                url = line.split('=', 1)[1]
                # 提取端口 http://localhost:8000/api -> 8000
                if ':' in url and '/api' in url:
                    frontend_api_host = url.split(':')[2].split('/')[0]
            elif line.startswith('VITE_WS_URL='):
                url = line.split('=', 1)[1]
                # 提取端口 ws://localhost:8000/ws -> 8000
                if ':' in url and '/ws' in url:
                    frontend_ws_host = url.split(':')[2].split('/')[0]

        print(f"[PORT] 端口配置检查:")
        print(f"   - 后端服务端口 (API_PORT): {backend_port}")
        print(f"   - 前端 API 连接端口: {frontend_api_host}")
        print(f"   - 前端 WS 连接端口: {frontend_ws_host}")

        # 检查一致性
        if backend_port and frontend_api_host and frontend_ws_host:
            if (backend_port == frontend_api_host == frontend_ws_host):
                print(f"[SUCCESS] 端口配置一致")
                return True
            else:
                print(f"[WARNING] 端口配置不一致")
                return False
        else:
            print(f"[ERROR] 缺少端口配置信息")
            return False

    except Exception as e:
        print(f"[ERROR] 端口配置检查失败: {e}")
        return False

def main():
    """主函数"""
    print("[TEST] 开始配置验证")

    results = []

    # 验证后端配置
    results.append(("后端配置", verify_backend_config()))

    # 验证前端配置
    results.append(("前端配置", verify_frontend_config()))

    # 验证端口一致性
    results.append(("端口一致性", verify_port_consistency()))

    # 显示结果摘要
    print_section("验证结果摘要")

    success_count = 0
    for name, success in results:
        status = "[PASS] 通过" if success else "[FAIL] 失败"
        print(f"   {name}: {status}")
        if success:
            success_count += 1

    print(f"\n[SUMMARY] 总体结果: {success_count}/{len(results)} 项验证通过")

    if success_count == len(results):
        print("[COMPLETE] 所有配置验证通过！前后端配置统一成功。")
        return 0
    else:
        print("[WARNING] 存在配置问题，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
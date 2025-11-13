#!/usr/bin/env python3
"""
配置验证脚本
验证优化后的环境变量配置是否正确
"""

import os
import sys
from pathlib import Path

def check_env_variables():
    """检查环境变量配置"""
    print("=" * 50)
    print("环境变量配置检查")
    print("=" * 50)

    # 检查 demo/.env 文件
    env_path = Path(__file__).parent / ".env"
    if not env_path.exists():
        print(f"❌ 找不到 .env 文件: {env_path}")
        return False

    print(f"[SUCCESS] 找到 .env 文件: {env_path}")

    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv(env_path)

    # 检查核心配置
    required_vars = {
        "ZHIPU_API_KEY": "智谱AI API密钥",
        "ZHIPU_BASE_URL": "智谱AI基础URL",
        "ZHIPU_MODEL": "智谱AI模型"
    }

    all_good = True
    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            if var == "ZHIPU_API_KEY":
                masked = value[:4] + "***" + value[-4:] if len(value) > 8 else "***"
                print(f"[SUCCESS] {var} ({desc}): {masked}")
            else:
                print(f"[SUCCESS] {var} ({desc}): {value}")
        else:
            print(f"[ERROR] {var} ({desc}): 未设置")
            all_good = False

    # 检查兼容性变量
    print(f"\n[INFO] 兼容性变量检查:")
    compat_vars = {
        "OPENAI_API_KEY": "兼容性API密钥",
        "OPENAI_BASE_URL": "兼容性基础URL",
        "LLM_MODEL": "兼容性模型",
        "DEFAULT_MODEL": "兼容性默认模型"
    }

    for var, desc in compat_vars.items():
        value = os.getenv(var)
        if value:
            print(f"[SUCCESS] {var} ({desc}): 已设置")
        else:
            print(f"[WARNING] {var} ({desc}): 未设置")

    return all_good

def check_config_consistency():
    """检查配置一致性"""
    print("\n" + "=" * 50)
    print("配置一致性检查")
    print("=" * 50)

    # 检查模型一致性
    zhipu_model = os.getenv('ZHIPU_MODEL')
    llm_model = os.getenv('LLM_MODEL')
    default_model = os.getenv('DEFAULT_MODEL')

    print(f"模型配置:")
    print(f"  ZHIPU_MODEL: {zhipu_model}")
    print(f"  LLM_MODEL: {llm_model}")
    print(f"  DEFAULT_MODEL: {default_model}")

    # 检查API密钥一致性
    zhipu_key = os.getenv('ZHIPU_API_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')

    print(f"\nAPI密钥配置:")
    if zhipu_key and openai_key:
        if zhipu_key == openai_key:
            print(f"  [SUCCESS] ZHIPU_API_KEY 和 OPENAI_API_KEY 一致")
        else:
            print(f"  [ERROR] ZHIPU_API_KEY 和 OPENAI_API_KEY 不一致")

    # 检查URL一致性
    zhipu_url = os.getenv('ZHIPU_BASE_URL')
    openai_url = os.getenv('OPENAI_BASE_URL')

    print(f"\n[INFO] URL配置:")
    if zhipu_url and openai_url:
        if zhipu_url == openai_url:
            print(f"  [SUCCESS] ZHIPU_BASE_URL 和 OPENAI_BASE_URL 一致")
        else:
            print(f"  [ERROR] ZHIPU_BASE_URL 和 OPENAI_BASE_URL 不一致")

def check_backend_config():
    """检查后端配置加载"""
    print("\n" + "=" * 50)
    print("后端配置加载检查")
    print("=" * 50)

    try:
        # 添加后端路径
        backend_path = Path(__file__).parent / "web_interface" / "backend"
        sys.path.insert(0, str(backend_path))

        from app.core.config import settings

        print(f"[SUCCESS] 后端配置加载成功:")
        print(f"  API_HOST: {settings.api_host}")
        print(f"  API_PORT: {settings.api_port}")
        print(f"  API_DEBUG: {settings.api_debug}")
        print(f"  LLM_MODEL: {settings.llm_model}")
        print(f"  OPENAI_API_KEY: {'已设置' if settings.openai_api_key else '未设置'}")
        print(f"  OPENAI_BASE_URL: {settings.openai_base_url}")

        return True

    except Exception as e:
        print(f"[ERROR] 后端配置加载失败: {e}")
        return False

def check_frontend_config():
    """检查前端环境变量"""
    print("\n" + "=" * 50)
    print("前端环境变量检查")
    print("=" * 50)

    env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        print(f"[ERROR] 找不到 .env 文件")
        return False

    # 读取环境变量
    vite_vars = {}
    try:
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    if key.startswith('VITE_'):
                        vite_vars[key] = value
    except Exception as e:
        print(f"[ERROR] 读取环境变量失败: {e}")
        return False

    print(f"前端环境变量 ({len(vite_vars)} 个):")

    # 关键前端变量
    key_vars = [
        'VITE_API_BASE_URL',
        'VITE_WS_URL',
        'VITE_DEFAULT_MODEL',
        'VITE_ZHIPU_BASE_URL',
        'VITE_APP_NAME',
        'VITE_ENVIRONMENT',
        'VITE_DEBUG'
    ]

    for var in key_vars:
        value = vite_vars.get(var, '未设置')
        if var == 'VITE_DEFAULT_MODEL' and value != '未设置':
            # 处理变量引用
            if value.startswith('${') and value.endswith('}'):
                ref_var = value[2:-1]
                ref_value = os.getenv(ref_var, '未设置')
                print(f"  {var}: {value} -> {ref_value}")
            else:
                print(f"  {var}: {value}")
        else:
            print(f"  {var}: {value}")

    return True

def main():
    """主函数"""
    print("[TEST] 配置验证开始")

    results = []

    # 检查环境变量
    results.append(("环境变量配置", check_env_variables()))

    # 检查配置一致性
    check_config_consistency()

    # 检查后端配置
    results.append(("后端配置加载", check_backend_config()))

    # 检查前端配置
    results.append(("前端环境变量", check_frontend_config()))

    # 显示结果
    print("\n" + "=" * 50)
    print("验证结果摘要")
    print("=" * 50)

    success_count = 0
    for name, success in results:
        status = "[PASS] 通过" if success else "[FAIL] 失败"
        print(f"  {name}: {status}")
        if success:
            success_count += 1

    print(f"\n[SUMMARY] 总体结果: {success_count}/{len(results)} 项检查通过")

    if success_count == len(results):
        print("[COMPLETE] 所有配置验证通过！")
        return 0
    else:
        print("[WARNING] 存在配置问题，请检查上述错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
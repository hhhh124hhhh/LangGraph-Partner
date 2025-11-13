from typing import Optional
from pathlib import Path
import os

from fastapi import APIRouter, Depends
from openai import OpenAI

from app.core.config import settings
from app.core.security import rate_limit_dependency
from app.models.response import SuccessResponse

router = APIRouter()

@router.get("/model")
async def get_model(_: None = Depends(rate_limit_dependency)):
    return SuccessResponse(success=True, message="ok", data={
        "model": settings.llm_model,
        "env": {
            "LLM_MODEL": os.environ.get("LLM_MODEL"),
            "DEFAULT_MODEL": os.environ.get("DEFAULT_MODEL")
        }
    })

def _write_env(model: str):
    project_root = Path(__file__).parent.parent.parent.parent.parent
    env_path = project_root / ".env"
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    found_llm = False
    found_default = False
    new_lines = []
    for line in lines:
        if line.startswith("LLM_MODEL="):
            new_lines.append(f"LLM_MODEL={model}")
            found_llm = True
        elif line.startswith("DEFAULT_MODEL="):
            new_lines.append(f"DEFAULT_MODEL={model}")
            found_default = True
        else:
            new_lines.append(line)
    if not found_llm:
        new_lines.append(f"LLM_MODEL={model}")
    if not found_default:
        new_lines.append(f"DEFAULT_MODEL={model}")
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ["LLM_MODEL"] = model
    os.environ["DEFAULT_MODEL"] = model

@router.put("/model")
async def set_model(payload: dict, _: None = Depends(rate_limit_dependency)):
    model = str(payload.get("model", "")).strip()
    if not model:
        return SuccessResponse(success=False, message="invalid model", data={})
    settings.llm_model = model
    _write_env(model)
    return SuccessResponse(success=True, message="updated", data={
        "model": settings.llm_model
    })

def _write_env_kv(k: str, v: str):
    project_root = Path(__file__).parent.parent.parent.parent.parent
    env_path = project_root / ".env"
    lines = []
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    found = False
    new_lines = []
    for line in lines:
        if line.startswith(f"{k}="):
            new_lines.append(f"{k}={v}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{k}={v}")
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    os.environ[k] = v

@router.get("/config")
async def get_config(_: None = Depends(rate_limit_dependency)):
    # 检查环境变量中的配置
    env_zhipu_key = os.environ.get("ZHIPU_API_KEY")
    env_openai_key = os.environ.get("OPENAI_API_KEY")
    env_zhipu_url = os.environ.get("ZHIPU_BASE_URL")
    env_openai_url = os.environ.get("OPENAI_BASE_URL")
    env_llm_model = os.environ.get("LLM_MODEL")
    env_default_model = os.environ.get("DEFAULT_MODEL")
    
    # 确定最终值和来源
    api_key_source = "env" if env_zhipu_key or env_openai_key else "config"
    api_key = env_zhipu_key or env_openai_key or settings.openai_api_key
    
    base_url_source = "env" if env_zhipu_url or env_openai_url else "config"
    base_url = env_zhipu_url or env_openai_url or settings.openai_base_url
    
    model_source = "env" if env_llm_model or env_default_model else "config"
    model = env_llm_model or env_default_model or settings.llm_model
    
    # API密钥遮掩显示
    masked_api_key = None
    if api_key and len(api_key) > 8:
        masked_api_key = api_key[:4] + "***" + api_key[-4:]
    elif api_key:
        masked_api_key = "***"
        
    return SuccessResponse(success=True, message="ok", data={
        "api_key": masked_api_key,
        "base_url": base_url,
        "model": model,
        "sources": {
            "api_key": api_key_source,
            "base_url": base_url_source,
            "model": model_source
        },
        "has_env_config": api_key_source == "env" or base_url_source == "env" or model_source == "env",
        "env_status": "已加载" if api_key_source == "env" else "未配置"
    })

@router.put("/config")
async def set_config(payload: dict, _: None = Depends(rate_limit_dependency)):
    api_key = payload.get("api_key")
    base_url = payload.get("base_url")
    model = payload.get("model")
    if isinstance(api_key, str) and api_key.strip():
        settings.openai_api_key = api_key.strip()
        _write_env_kv("ZHIPU_API_KEY", settings.openai_api_key)
        _write_env_kv("OPENAI_API_KEY", settings.openai_api_key)
    if isinstance(base_url, str) and base_url.strip():
        settings.openai_base_url = base_url.strip()
        _write_env_kv("ZHIPU_BASE_URL", settings.openai_base_url)
        _write_env_kv("OPENAI_BASE_URL", settings.openai_base_url)
    if isinstance(model, str) and model.strip():
        settings.llm_model = model.strip()
        _write_env(settings.llm_model)
    return SuccessResponse(success=True, message="updated", data={
        "api_key": settings.openai_api_key,
        "base_url": settings.openai_base_url,
        "model": settings.llm_model
    })

def _fetch_models(api_key: str, base_url: str):
    try:
        client = OpenAI(api_key=api_key, base_url=base_url)
        res = client.models.list()
        items = getattr(res, "data", [])
        ids = [getattr(m, "id", "") for m in items if getattr(m, "id", "")]
        if ids:
            return True, ids
        return True, [
            "glm-4-flash",        # 免费模型，速度快
            "glm-4-air",          # 免费模型，性价比高
            "glm-4",              # 基础模型
            "glm-4-plus",         # 增强模型
            "glm-4-long",         # 长上下文模型
            "glm-4x",             # 最新版本
            "glm-4v",             # 视觉模型
            "glm-4-alltools",     # 工具调用模型
            "glm-3-turbo",        # 轻量级模型
            "embedding-2",        # 嵌入模型
            "embedding-3"         # 最新嵌入模型
        ]
    except Exception:
        return False, ["glm-4-flash", "glm-4.6", "glm-4-plus"]

@router.post("/validate")
async def validate_and_list_models(payload: dict | None = None, _: None = Depends(rate_limit_dependency)):
    api_key = (payload or {}).get("api_key") or os.environ.get("ZHIPU_API_KEY") or os.environ.get("OPENAI_API_KEY") or settings.openai_api_key
    base_url = (payload or {}).get("base_url") or os.environ.get("ZHIPU_BASE_URL") or os.environ.get("OPENAI_BASE_URL") or settings.openai_base_url
    valid, models = _fetch_models(api_key, base_url)
    source_info = "API动态获取" if valid else "备用模型列表（智谱AI兼容）"
    
    free_models = [m for m in models if "flash" in m or "air" in m or "turbo" in m]
    
    return SuccessResponse(success=True, message="ok", data={
        "valid": valid,
        "models": models,
        "source": source_info,
        "total_count": len(models),
        "free_models": free_models,
        "message": f"获取到{len(models)}个模型，包含免费模型: {len(free_models)}个"
    })

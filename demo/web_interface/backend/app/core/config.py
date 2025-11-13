"""
FastAPI 应用配置
使用 Pydantic Settings 进行配置管理
"""

from typing import List, Optional, ClassVar
from pydantic import Field, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置类"""

    # API 配置
    api_host: str = Field(default="0.0.0.0", description="API服务器主机", alias="API_HOST")
    api_port: int = Field(default=8000, description="API服务器端口", alias="API_PORT")
    api_debug: bool = Field(default=True, description="调试模式", alias="API_DEBUG")
    api_reload: bool = Field(default=True, description="自动重载", alias="API_RELOAD")

    # CORS 配置 - 使用ClassVar避免Pydantic解析
    cors_origins: ClassVar[List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3004", "http://127.0.0.1:3004"]

    # 智谱AI API 配置
    openai_api_key: str = Field(default="", description="智谱AI API密钥", alias="OPENAI_API_KEY")
    ai_claude_api_key: Optional[str] = Field(None, description="AI Claude API密钥", alias="AI_CLAUDE_API_KEY")
    openai_base_url: str = Field(
        default="https://open.bigmodel.cn/api/paas/v4",
        description="OpenAI API基础URL",
        alias="OPENAI_BASE_URL"
    )

    # 数据存储路径
    vector_db_path: str = Field(default="./vector_db", description="向量数据库路径", alias="VECTOR_DB_PATH")
    memory_dir: str = Field(default="./memory", description="记忆存储目录", alias="MEMORY_DIR")
    config_dir: str = Field(default="./config", description="配置文件目录", alias="CONFIG_DIR")

    # 模型配置
    llm_model: str = Field(default="glm-4-flash", description="LLM模型名称", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=1.0, description="LLM温度参数", alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2000, ge=1, description="LLM最大令牌数", alias="LLM_MAX_TOKENS")

    # 日志配置
    log_level: str = Field(default="DEBUG", description="日志级别", alias="LOG_LEVEL")
    log_format: str = Field(default="text", description="日志格式", alias="LOG_FORMAT")

    # 会话配置
    default_session_timeout: int = Field(default=3600, description="默认会话超时时间（秒）", alias="DEFAULT_SESSION_TIMEOUT")
    max_context_turns: int = Field(default=10, ge=1, description="最大上下文轮次", alias="MAX_CONTEXT_TURNS")

    # 搜索配置
    default_search_results: int = Field(default=5, ge=1, description="默认搜索结果数量", alias="DEFAULT_SEARCH_RESULTS")
    min_similarity_score: float = Field(default=0.3, ge=0.0, le=1.0, description="最小相似度阈值", alias="MIN_SIMILARITY_SCORE")

    # 暂时注释掉cors_origins验证器，使用默认值
    # @validator("cors_origins", pre=True)
    # def parse_cors_origins(cls, v):
    #     """解析CORS源列表"""
    #     if isinstance(v, str):
    #         return [origin.strip() for origin in v.split(",")]
    #     return v

    @validator("log_level")
    def validate_log_level(cls, v):
        """验证日志级别"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"日志级别必须是以下之一: {valid_levels}")
        return v.upper()

    class Config:
        env_file = ["../../../.env"]  # 只从 demo/.env 加载配置
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"

    # Pydantic V2 使用 field_validator 替代 fields 映射
    # 环境变量别名直接在 Field 定义中设置

    def get_api_url(self) -> str:
        """获取API完整URL"""
        return f"http://{self.api_host}:{self.api_port}"

    def get_env_info(self) -> dict:
        """获取环境信息（用于调试）"""
        return {
            "environment": "development" if self.api_debug else "production",
            "api_url": self.get_api_url(),
            "llm_model": self.llm_model,
            "vector_db_path": self.vector_db_path,
            "memory_dir": self.memory_dir,
            "config_dir": self.config_dir
        }


# 全局配置实例
settings = Settings()
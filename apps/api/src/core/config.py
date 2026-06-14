"""配置中心：从环境变量读取所有运行参数。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "dev"

    # ---------- PostgreSQL ----------
    postgres_user: str = "wab"
    postgres_password: str = "wab"
    postgres_db: str = "wab"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    @property
    def database_url(self) -> str:
        """异步 SQLAlchemy URL（FastAPI 运行时用）"""
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        """同步 URL（Alembic 用）"""
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # ---------- MinIO ----------
    minio_endpoint: str = "minio:9000"
    minio_public_endpoint: str = "https://wab.ybgames.cn/files"
    minio_root_user: str = "wabadmin"
    minio_root_password: str = "wabadmin"
    minio_use_ssl: bool = False
    minio_bucket_uploads: str = "wab-uploads"
    minio_bucket_tts: str = "wab-tts"
    minio_bucket_pdfs: str = "wab-pdfs"

    # ---------- API / JWT ----------
    api_secret_key: str = "dev-secret-change-me-in-prod"
    api_jwt_algorithm: str = "HS256"
    api_jwt_expire_minutes: int = 10080  # 7 天
    api_cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.api_cors_origins.split(",") if o.strip()]

    # ---------- LLM: DeepSeek ----------
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model_text: str = "deepseek-chat"
    deepseek_model_vision: str = "deepseek-vl2"

    # ---------- LLM: Qwen 兜底 ----------
    qwen_api_key: str = ""
    qwen_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    qwen_model_vision: str = "qwen-vl-max"

    # ---------- TTS ----------
    tts_default_voice: str = "zh-CN-YunxiaNeural"
    tts_default_rate: str = "-10%"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()

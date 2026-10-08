from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "AI Enterprise Assistant"
    database_url: str = "postgresql+psycopg2://ai:ai@localhost:5432/aiassistant"
    readonly_database_url: str = ""  # opsional: user DB read-only khusus SQL Agent
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"

    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480
    admin_email: str = "admin@company.com"
    admin_password: str = "Admin123!"
    admin_name: str = "Administrator"
    auto_seed: bool = True

    # LLM: "mock" (tanpa API key, mode demo) atau "openai" (semua API OpenAI-compatible: OpenAI, Ollama, vLLM, Groq, dll)
    llm_provider: str = "mock"
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    llm_model: str = "gpt-4o-mini"
    price_per_1m_input: float = 0.15
    price_per_1m_output: float = 0.60

    # Embedding: "local" (hashing, tanpa download), "openai", atau "sentence_transformers"
    embedding_provider: str = "local"
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 384

    upload_dir: str = "/data/uploads"
    reports_dir: str = "/data/reports"
    max_upload_mb: int = 25
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_k: int = 5
    ocr_lang: str = "ind+eng"
    use_celery: bool = False
    rate_limit_per_minute: int = 120
    sql_max_rows: int = 200
    sql_timeout_ms: int = 5000
    agent_max_steps: int = 6


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

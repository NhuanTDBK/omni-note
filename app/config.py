from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    class Config:
        env_file = ".env"

    # Database
    DATABASE_URL: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB

    # Vector Database
    QDRANT_HOST: str
    QDRANT_PORT: int

    EMBEDDING_MODEL: str = "vidore/colqwen2-v1.0"

    AGENT_CATEGORIZATION_LLM_URL: str = "http://localhost:1234/v1"
    AGENT_CATEGORIZATION_LLM_API_KEY: str = "1234"
    AGENT_CATEGORIZATION_LLM_MODEL: str = "qwen2.5-vl-7b-instruct"

    AGENT_EXTRACTOR_LLM_URL: str = "http://localhost:1234/v1"
    AGENT_EXTRACTOR_LLM_API_KEY: str = "1234"
    AGENT_EXTRACTOR_LLM_MODEL: str = "qwen2.5-vl-7b-instruct"

    AGENT_SUMMARIZATION_LLM_URL: str = "http://localhost:1234/v1"
    AGENT_SUMMARIZATION_LLM_API_KEY: str = "1234"
    AGENT_SUMMARIZATION_LLM_MODEL: str = "qwen2.5-14b-instruct-mlx"


@lru_cache()
def get_settings():
    return Settings()

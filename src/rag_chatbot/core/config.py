from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "RAG Chatbot API"

    openai_api_key: str
    openai_model: str
    openai_embedding_model: str
    openai_temperature: float = 0.2

    chunk_size: int = 1000
    chunk_overlap: int = 100
    retrieval_k: int = 3

    max_upload_size_mb: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
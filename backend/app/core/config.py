from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, field_validator


class Settings(BaseSettings):
    APP_NAME: str = "Explainable Indian Constitutional Rights & Legal Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = "development_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8080",
        "*"
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./legal_assistant.db"

    # LLM & Local Ollama Configuration
    LLM_PROVIDER: str = "ollama"  # "ollama", "gemini", "openai", "deterministic"
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"  # or llama3.2, mistral, qwen2.5, phi3, etc.
    OLLAMA_TIMEOUT_SECONDS: int = 30

    # Legal Assistant Disclaimers
    DISCLAIMER_TEXT: str = (
        "This platform provides general educational and research information regarding "
        "the Constitution of India and Indian statutory legal provisions. "
        "It is not legal advice and does not substitute for consultation with a qualified legal professional."
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="allow"
    )


settings = Settings()

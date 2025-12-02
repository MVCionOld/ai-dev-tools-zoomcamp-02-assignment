"""Application settings loaded from environment variables."""

from __future__ import annotations

from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "Rivendell"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/rivendell"
    )
    TEST_DATABASE_URL: str | None = None
    DATABASE_POOL_SIZE: int = 20
    SQLALCHEMY_ECHO: bool = False

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PUBSUB_CHANNEL: str = "sharedb"

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    SESSION_EXPIRE_HOURS: int = 24
    ALLOWED_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://localhost:3000"]
    )

    # Code execution
    DOCKER_HOST: str = "unix:///var/run/docker.sock"
    EXECUTION_TIMEOUT: int = 10
    EXECUTION_MEMORY_LIMIT: str = "256m"
    PYTHON_EXECUTOR_IMAGE: str = "rivendell/python:3.13-executor"
    SUPPORTED_LANGUAGES: List[str] = Field(default_factory=lambda: ["python3.13"])
    PROBLEM_TEXT_MAX_LENGTH: int | None = 20000
    SESSION_CLEANUP_INTERVAL_SECONDS: int = 600

    LOG_LEVEL: str = "INFO"

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("SUPPORTED_LANGUAGES", mode="before")
    @classmethod
    def _split_supported_languages(cls, value: List[str] | str) -> List[str]:
        if isinstance(value, str):
            return [
                language.strip() for language in value.split(",") if language.strip()
            ]
        return value


settings = Settings()

"""Schemas for code execution requests."""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.config import settings


class ExecutionCreate(BaseModel):
    code: str = Field(..., min_length=1)
    language: str
    stdin: str | None = None
    timeout: int | None = None
    memory_limit: str | None = None

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"language '{value}' is not supported; options: {settings.SUPPORTED_LANGUAGES}"
            )
        return value

    @field_validator("timeout")
    @classmethod
    def validate_timeout(cls, value: int | None) -> int | None:
        if value is not None and value <= 0:
            raise ValueError("timeout must be a positive integer")
        return value


class ExecutionResultRead(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    memory_used_kb: int
    error: str | None = None
    session_id: UUID
    language: str


class Executor(BaseModel):
    language: str
    display_name: str
    description: str | None = None


class ExecutorList(BaseModel):
    executors: list[Executor]

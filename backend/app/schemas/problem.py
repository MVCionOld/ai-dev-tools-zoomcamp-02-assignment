"""Schemas for problem statement operations."""

from __future__ import annotations

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings
from app.schemas.session import SessionDetail


class ProblemUpdate(BaseModel):
    user_id: UUID
    problem_text: str = Field(..., description="Markdown problem statement")

    @field_validator("problem_text")
    @classmethod
    def validate_problem_text(cls, value: str) -> str:
        max_length = getattr(settings, "PROBLEM_TEXT_MAX_LENGTH", None)
        if max_length and len(value) > max_length:
            raise ValueError("problem_text exceeds maximum allowed length")
        return value


class ProblemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    problem_text: str | None = None


class ProblemBroadcast(BaseModel):
    session_id: UUID
    updated_by: UUID
    problem_text: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_session(cls, session: SessionDetail, user_id: UUID) -> "ProblemBroadcast":
        return cls(
            session_id=session.id,
            updated_by=user_id,
            problem_text=session.problem_text or "",
        )

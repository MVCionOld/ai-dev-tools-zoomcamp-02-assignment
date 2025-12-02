"""Schemas related to interview sessions."""

from __future__ import annotations

from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.config import settings
from app.models.session import UserRole


class SessionCreate(BaseModel):
    name: str = Field(..., max_length=255)
    language: str = Field(..., max_length=64)
    creator_id: UUID | None = None
    problem_text: str | None = None

    @field_validator("language")
    @classmethod
    def validate_language(cls, value: str) -> str:
        if value not in settings.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"language '{value}' is not supported; options: {settings.SUPPORTED_LANGUAGES}"
            )
        return value


class SessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    language: str
    created_at: datetime
    expires_at: datetime
    creator_id: UUID | None = None
    code_snapshot: str | None = None
    problem_text: str | None = None
    is_active: bool


class SessionList(BaseModel):
    items: List["SessionDetail"]


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: UserRole
    joined_at: datetime
    last_seen: datetime


class SessionDetail(SessionRead):
    users: List[UserRead] = Field(default_factory=list)


class SessionJoinRequest(BaseModel):
    user_id: UUID | None = None

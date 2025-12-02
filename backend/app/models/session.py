"""Database models for collaborative coding sessions."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import CHAR, TypeDecorator

from app.db.base import Base


class GUID(TypeDecorator):
    """Platform-independent GUID type."""

    impl = PG_UUID
    cache_ok = True

    def load_dialect_impl(self, dialect):  # type: ignore[override]
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID(as_uuid=True))
        return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):  # type: ignore[override]
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return str(value)
        return str(uuid.UUID(str(value)))

    def process_result_value(self, value, dialect):  # type: ignore[override]
        if value is None:
            return value
        return uuid.UUID(str(value))


class UserRole(str, Enum):
    CREATOR = "creator"
    PARTICIPANT = "participant"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    language: Mapped[str] = mapped_column(String(64), nullable=False)
    code_snapshot: Mapped[str | None] = mapped_column(Text())
    problem_text: Mapped[str | None] = mapped_column(Text())
    creator_id: Mapped[uuid.UUID | None] = mapped_column(GUID(), ForeignKey("users.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    users: Mapped[list[User]] = relationship(
        "User",
        back_populates="session",
        cascade="all, delete-orphan",
        foreign_keys="User.session_id",
    )
    creator: Mapped[User | None] = relationship(
        "User", foreign_keys=[creator_id], post_update=True
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("sessions.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow
    )

    session: Mapped[Session] = relationship(
        "Session",
        back_populates="users",
        foreign_keys=[session_id],
    )

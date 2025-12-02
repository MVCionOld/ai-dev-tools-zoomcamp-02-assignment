"""Shared FastAPI dependencies."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, settings
from app.db.session import AsyncSessionFactory, get_session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for request handling."""

    async with AsyncSessionFactory() as session:
        yield session


def get_settings() -> Settings:
    """Provide application settings for injection."""

    return settings


async def get_readonly_session(
    session: AsyncSession = Depends(get_session),
) -> AsyncGenerator[AsyncSession, None]:
    """Return a session that rolls back any changes after use."""

    try:
        yield session
    finally:
        await session.rollback()

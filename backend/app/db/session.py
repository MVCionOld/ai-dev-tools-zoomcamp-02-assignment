"""Database session management utilities."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def _build_engine(database_url: str | None = None) -> AsyncEngine:
    url = database_url or settings.DATABASE_URL
    return create_async_engine(url, echo=settings.SQLALCHEMY_ECHO)


engine: AsyncEngine = _build_engine()
AsyncSessionFactory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session

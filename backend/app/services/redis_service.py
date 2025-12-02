"""Redis connection helpers."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    pass

# Need actual imports for runtime
import redis.asyncio  # type: ignore[import-untyped]
import redis.exceptions  # type: ignore[import-untyped]

from app.core.config import settings

_redis_client: Optional[redis.asyncio.Redis] = None  # type: ignore[name-defined]


async def get_redis_client() -> redis.asyncio.Redis:  # type: ignore[name-defined]
    """Lazily create and return a shared Redis client."""
    global _redis_client
    if _redis_client is None:
        # Use FakeRedis in testing mode
        if settings.TESTING:
            from fakeredis.aioredis import FakeRedis  # type: ignore

            _redis_client = FakeRedis(decode_responses=True)
        else:
            _redis_client = redis.asyncio.Redis.from_url(  # type: ignore[attr-defined]
                settings.REDIS_URL, decode_responses=True
            )
            try:
                ping_result = _redis_client.ping()
                if asyncio.iscoroutine(ping_result):
                    await ping_result
            except (redis.exceptions.ConnectionError, OSError):  # type: ignore[attr-defined]
                from fakeredis.aioredis import FakeRedis  # type: ignore

                _redis_client = FakeRedis(decode_responses=True)
    return _redis_client


async def close_redis_client() -> None:
    """Close the shared Redis client if it exists."""
    global _redis_client
    if _redis_client is not None:
        close_method = getattr(_redis_client, "aclose", None)
        if close_method is not None:
            await close_method()
        else:
            close_result = _redis_client.close()
            if asyncio.iscoroutine(close_result):
                await close_result
        _redis_client = None

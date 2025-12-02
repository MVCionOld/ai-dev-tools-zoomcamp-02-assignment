"""Helpers for broadcasting real-time events."""

from __future__ import annotations

import json
from typing import Any

from app.core.config import settings
from app.schemas.problem import ProblemBroadcast
from app.services.redis_service import get_redis_client
from app.websocket.connection_manager import connection_manager


_ORIGIN_ID = connection_manager.origin_id


async def publish_event(message: dict[str, Any]) -> None:
    message = dict(message)
    meta = message.setdefault("meta", {})
    meta.setdefault("origin", _ORIGIN_ID)
    redis = await get_redis_client()
    await redis.publish(settings.REDIS_PUBSUB_CHANNEL, json.dumps(message, default=str))


async def broadcast_problem_update(event: ProblemBroadcast) -> None:
    payload = event.model_dump()
    message = {
        "type": "problem_updated",
        "data": payload,
        "meta": {"origin": _ORIGIN_ID},
    }
    await connection_manager.broadcast(event.session_id, message)
    await publish_event(message)

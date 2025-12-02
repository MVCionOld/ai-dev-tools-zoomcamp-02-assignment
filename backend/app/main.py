"""FastAPI application entry point."""

from __future__ import annotations

import asyncio
import json
import logging
from contextlib import asynccontextmanager, suppress
from typing import Awaitable
from uuid import UUID

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.core.config import settings
from app.db.session import AsyncSessionFactory
from app.services.redis_service import close_redis_client, get_redis_client
from app.services.session_service import cleanup_expired_sessions
from app.websocket.connection_manager import connection_manager
from app.websocket.sharedb_integration import ShareDBHandler

logger = logging.getLogger(__name__)


async def _session_cleanup_loop() -> None:
    interval = max(1, settings.SESSION_CLEANUP_INTERVAL_SECONDS)
    while True:
        try:
            async with AsyncSessionFactory() as session:
                await cleanup_expired_sessions(session)
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            raise
        except Exception as exc:  # noqa: BLE001 - log and continue
            logger.warning("Session cleanup loop error: %s", exc)
        await asyncio.sleep(interval)


async def _redis_listener_loop() -> None:
    while True:
        pubsub = None
        try:
            redis = await get_redis_client()
            pubsub = redis.pubsub(ignore_subscribe_messages=True)
            await pubsub.subscribe(settings.REDIS_PUBSUB_CHANNEL)
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                raw = message.get("data")
                if not raw:
                    continue
                try:
                    payload = json.loads(raw)
                except json.JSONDecodeError:
                    logger.debug("Ignored malformed pubsub payload: %s", raw)
                    continue
                meta = payload.get("meta", {})
                if meta.get("origin") == connection_manager.origin_id:
                    continue

                event_type = payload.get("type")
                if event_type != "problem_updated":
                    continue
                data = payload.get("data", {})
                session_id_value = data.get("session_id")
                if session_id_value is None:
                    continue
                try:
                    session_uuid = UUID(str(session_id_value))
                except ValueError:
                    logger.debug("Invalid session_id in event: %s", session_id_value)
                    continue
                await connection_manager.broadcast(session_uuid, payload)
        except asyncio.CancelledError:  # pragma: no cover - cancellation path
            raise
        except Exception as exc:  # noqa: BLE001 - log and retry
            logger.warning("Redis listener error: %s", exc)
            await asyncio.sleep(5)
        finally:
            if pubsub is not None:
                close_method = getattr(pubsub, "aclose", None)
                if close_method is not None:
                    await close_method()
                else:
                    await pubsub.close()
        await asyncio.sleep(0)


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):  # pragma: no cover - exercised during startup/shutdown
    """Application lifespan hook for shared resources."""

    tasks: list[asyncio.Task] = []
    try:
        redis = await get_redis_client()
        ping_result = redis.ping()
        if isinstance(ping_result, Awaitable):
            await ping_result
    except Exception as exc:  # noqa: BLE001 - log and continue for local development
        logger.warning("Redis ping failed during startup: %s", exc)

    tasks.append(asyncio.create_task(_session_cleanup_loop()))
    tasks.append(asyncio.create_task(_redis_listener_loop()))
    yield
    for task in tasks:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task
    await close_redis_client()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.websocket("/ws/sessions/{session_id}")
async def session_websocket(websocket: WebSocket, session_id: str) -> None:
    try:
        session_uuid = UUID(session_id)
    except ValueError:
        await websocket.close(code=1003)
        return

    # Connect with generated connection_id
    connection_id = await connection_manager.connect(session_uuid, websocket)

    # Extract user_id from query params if available
    user_id = None
    if websocket.query_params:
        user_id = websocket.query_params.get("user_id")

    try:
        while True:
            data = await websocket.receive_text()

            # Check if this is a ShareDB message
            if data.startswith("{"):
                try:
                    import json

                    message = json.loads(data)
                    msg_type = message.get("type")

                    # Handle ShareDB messages
                    if msg_type in [
                        "fetch",
                        "subscribe",
                        "unsubscribe",
                        "op",
                        "history",
                    ]:
                        response = await ShareDBHandler.handle_sharedb_message(
                            data, connection_id, str(session_uuid), user_id
                        )
                        if response:
                            await websocket.send_json(response)
                        continue
                except (json.JSONDecodeError, ValueError):
                    pass

            # Handle regular messages as before
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue

            message.setdefault("session_id", str(session_uuid))
            await connection_manager.broadcast(session_uuid, message, sender=websocket)

    except WebSocketDisconnect:
        await connection_manager.disconnect(session_uuid, websocket, connection_id)


@app.get("/health", tags=["health"])
async def health_check() -> dict[str, str]:
    """Return service availability status for health probes."""

    return {"status": "healthy"}


@app.get("/", tags=["root"])
async def root() -> dict[str, str]:
    """Simple greeting endpoint confirming API is reachable."""

    return {"message": "Welcome to Rivendell API"}

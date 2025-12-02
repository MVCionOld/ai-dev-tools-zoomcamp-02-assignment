"""In-memory connection manager for session WebSocket clients."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import DefaultDict, Set
from uuid import UUID, uuid4

from fastapi import WebSocket


class SessionConnectionManager:
    def __init__(self) -> None:
        self._connections: DefaultDict[UUID, Set[WebSocket]] = defaultdict(set)
        self._connection_map: dict[str, WebSocket] = {}  # connection_id -> websocket
        self._lock = asyncio.Lock()
        self.origin_id = str(uuid4())

    async def connect(
        self, session_id: UUID, websocket: WebSocket, connection_id: str | None = None
    ) -> str:
        """Connect a websocket to a session. Returns the connection_id."""
        if connection_id is None:
            connection_id = str(uuid4())

        await websocket.accept()
        async with self._lock:
            self._connections[session_id].add(websocket)
            self._connection_map[connection_id] = websocket

        await self.broadcast(
            session_id,
            {
                "type": "user_join",
                "data": {
                    "session_id": str(session_id),
                    "connections": await self.active_connections(session_id),
                },
            },
            sender=websocket,
        )

        return connection_id

    async def disconnect(
        self, session_id: UUID, websocket: WebSocket, connection_id: str | None = None
    ) -> None:
        async with self._lock:
            connections = self._connections.get(session_id)
            if connections and websocket in connections:
                connections.remove(websocket)
                if not connections:
                    self._connections.pop(session_id, None)

            if connection_id and connection_id in self._connection_map:
                del self._connection_map[connection_id]

        await self.broadcast(
            session_id,
            {
                "type": "user_leave",
                "data": {
                    "session_id": str(session_id),
                    "connections": await self.active_connections(session_id),
                },
            },
        )

    async def broadcast(
        self,
        session_id: UUID,
        message: dict,
        sender: WebSocket | None = None,
    ) -> None:
        async with self._lock:
            connections = list(self._connections.get(session_id, set()))
        for connection in connections:
            if sender is not None and connection is sender:
                continue
            try:
                await connection.send_json(message)
            except RuntimeError:  # pragma: no cover - client disconnected mid-send
                continue

    async def send_to_connection(
        self,
        connection_id: str,
        message: dict,
    ) -> bool:
        """Send a message to a specific connection by ID. Returns True if successful."""
        async with self._lock:
            websocket = self._connection_map.get(connection_id)

        if not websocket:
            return False

        try:
            await websocket.send_json(message)
            return True
        except RuntimeError:
            return False

    async def active_connections(self, session_id: UUID) -> int:
        async with self._lock:
            return len(self._connections.get(session_id, set()))


connection_manager = SessionConnectionManager()

"""
ShareDB integration with Redis backend for real-time collaborative editing.

This module provides a ShareDB-compatible implementation using Redis as the backend.
It handles Operational Transformation (OT) for conflict-free collaborative editing
of code and problem statements.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.services.redis_service import get_redis_client

logger = logging.getLogger(__name__)


@dataclass
class Operation:
    """Represents an operational transformation operation."""

    type: str  # "insert" or "delete"
    position: int
    content: str | None = None
    version: int = 0
    user_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type,
            "position": self.position,
            "content": self.content,
            "version": self.version,
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Operation:
        return cls(
            type=data["type"],
            position=data["position"],
            content=data.get("content"),
            version=data.get("version", 0),
            user_id=data.get("user_id"),
            timestamp=datetime.fromisoformat(
                data.get("timestamp", datetime.utcnow().isoformat())
            ),
        )


@dataclass
class ShareDBDocument:
    """Represents a ShareDB document (e.g., session code or problem text)."""

    collection: str  # e.g., "code", "problem"
    doc_id: str  # e.g., session_id
    version: int = 0
    content: str = ""
    operations: list[Operation] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "collection": self.collection,
            "doc_id": self.doc_id,
            "version": self.version,
            "content": self.content,
            "operations": [
                op.to_dict() for op in self.operations[-100:]
            ],  # Keep last 100 ops
            "created_at": self.created_at.isoformat(),
        }


class ShareDBService:
    """
    Service for managing ShareDB documents with Redis backend.

    Handles:
    - Document creation and lifecycle
    - Operational transformation for conflict resolution
    - Operation history and versioning
    - Real-time synchronization via WebSocket
    """

    # In-memory document store (in production, this would be Redis)
    _documents: dict[str, ShareDBDocument] = {}
    _subscribers: dict[str, set[str]] = {}  # doc_key -> set of connection_ids

    REDIS_PREFIX = "sharedb:"
    OPS_PREFIX = f"{REDIS_PREFIX}ops:"
    DOCS_PREFIX = f"{REDIS_PREFIX}docs:"
    SUBS_PREFIX = f"{REDIS_PREFIX}subs:"

    @classmethod
    async def create_document(
        cls,
        collection: str,
        doc_id: str,
        initial_content: str = "",
    ) -> ShareDBDocument:
        """Create a new ShareDB document."""
        doc = ShareDBDocument(
            collection=collection,
            doc_id=doc_id,
            content=initial_content,
        )

        redis = await get_redis_client()
        doc_key = f"{cls.DOCS_PREFIX}{collection}:{doc_id}"

        # Store document in Redis
        await redis.set(doc_key, json.dumps(doc.to_dict()))

        # Store in memory cache
        cls._documents[f"{collection}:{doc_id}"] = doc

        logger.info(f"Created ShareDB document: {collection}:{doc_id}")
        return doc

    @classmethod
    async def get_document(
        cls,
        collection: str,
        doc_id: str,
    ) -> ShareDBDocument | None:
        """Fetch a ShareDB document."""
        redis = await get_redis_client()
        doc_key = f"{cls.DOCS_PREFIX}{collection}:{doc_id}"

        # Check memory cache first
        cache_key = f"{collection}:{doc_id}"
        if cache_key in cls._documents:
            return cls._documents[cache_key]

        # Fetch from Redis
        data = await redis.get(doc_key)
        if not data:
            return None

        doc_data = json.loads(data)
        doc = ShareDBDocument(
            collection=doc_data["collection"],
            doc_id=doc_data["doc_id"],
            version=doc_data["version"],
            content=doc_data["content"],
        )

        # Cache in memory
        cls._documents[cache_key] = doc
        return doc

    @classmethod
    async def apply_operation(
        cls,
        collection: str,
        doc_id: str,
        operation: Operation,
    ) -> bool:
        """
        Apply an operation to a document using Operational Transformation.

        Returns True if successful, False if version conflict.
        """
        doc = await cls.get_document(collection, doc_id)
        if not doc:
            logger.warning(f"Document not found: {collection}:{doc_id}")
            return False

        # Version conflict check
        if operation.version != doc.version:
            logger.warning(
                f"Version conflict for {collection}:{doc_id}: "
                f"expected {doc.version}, got {operation.version}"
            )
            return False

        # Apply operation
        if operation.type == "insert":
            if operation.content is not None:
                doc.content = (
                    doc.content[: operation.position]
                    + operation.content
                    + doc.content[operation.position :]
                )
        elif operation.type == "delete":
            # For delete, we need a length in the operation
            length = len(operation.content) if operation.content else 1
            doc.content = (
                doc.content[: operation.position]
                + doc.content[operation.position + length :]
            )

        # Update version
        doc.version += 1
        operation.version = doc.version
        doc.operations.append(operation)

        # Persist to Redis
        redis = await get_redis_client()
        doc_key = f"{cls.DOCS_PREFIX}{collection}:{doc_id}"
        ops_key = f"{cls.OPS_PREFIX}{collection}:{doc_id}"

        await redis.set(doc_key, json.dumps(doc.to_dict()))
        await redis.lpush(ops_key, json.dumps(operation.to_dict()))

        # Publish to subscribers
        await cls._publish_operation(collection, doc_id, operation)

        logger.info(
            f"Applied operation to {collection}:{doc_id} "
            f"(v{doc.version}): {operation.type} at pos {operation.position}"
        )
        return True

    @classmethod
    async def _publish_operation(
        cls,
        collection: str,
        doc_id: str,
        operation: Operation,
    ) -> None:
        """Publish operation to subscribers."""
        redis = await get_redis_client()
        channel = f"{cls.REDIS_PREFIX}{collection}:{doc_id}"

        message = {
            "type": "op",
            "collection": collection,
            "doc_id": doc_id,
            "operation": operation.to_dict(),
        }

        await redis.publish(channel, json.dumps(message, default=str))

    @classmethod
    async def subscribe(
        cls,
        collection: str,
        doc_id: str,
        connection_id: str,
    ) -> None:
        """Subscribe a connection to document changes."""
        doc_key = f"{collection}:{doc_id}"

        if doc_key not in cls._subscribers:
            cls._subscribers[doc_key] = set()

        cls._subscribers[doc_key].add(connection_id)
        logger.info(f"Subscribed {connection_id} to {doc_key}")

    @classmethod
    async def unsubscribe(
        cls,
        collection: str,
        doc_id: str,
        connection_id: str,
    ) -> None:
        """Unsubscribe a connection from document changes."""
        doc_key = f"{collection}:{doc_id}"

        if doc_key in cls._subscribers:
            cls._subscribers[doc_key].discard(connection_id)
            logger.info(f"Unsubscribed {connection_id} from {doc_key}")

    @classmethod
    def get_subscribers(cls, collection: str, doc_id: str) -> set[str]:
        """Get all subscribers to a document."""
        doc_key = f"{collection}:{doc_id}"
        return cls._subscribers.get(doc_key, set()).copy()

    @classmethod
    async def get_operation_history(
        cls,
        collection: str,
        doc_id: str,
        from_version: int = 0,
    ) -> list[Operation]:
        """Fetch operation history from a specific version."""
        redis = await get_redis_client()
        ops_key = f"{cls.OPS_PREFIX}{collection}:{doc_id}"

        # Get all operations (they're stored in reverse order due to lpush)
        ops_data = await redis.lrange(ops_key, 0, -1)

        if not ops_data:
            return []

        operations = [Operation.from_dict(json.loads(op)) for op in ops_data]
        # Reverse to get chronological order
        operations.reverse()

        # Filter by version
        return [op for op in operations if op.version > from_version]

    @classmethod
    async def clear_document(
        cls,
        collection: str,
        doc_id: str,
    ) -> None:
        """Delete a document and its history."""
        redis = await get_redis_client()
        doc_key = f"{cls.DOCS_PREFIX}{collection}:{doc_id}"
        ops_key = f"{cls.OPS_PREFIX}{collection}:{doc_id}"
        cache_key = f"{collection}:{doc_id}"

        await redis.delete(doc_key)
        await redis.delete(ops_key)

        if cache_key in cls._documents:
            del cls._documents[cache_key]

        logger.info(f"Cleared ShareDB document: {collection}:{doc_id}")

    @classmethod
    async def get_presence(
        cls,
        collection: str,
        doc_id: str,
    ) -> dict[str, Any]:
        """Get presence information for a document."""
        redis = await get_redis_client()
        presence_key = f"{cls.REDIS_PREFIX}presence:{collection}:{doc_id}"

        data = await redis.get(presence_key)
        if not data:
            return {}

        return json.loads(data)

    @classmethod
    async def update_presence(
        cls,
        collection: str,
        doc_id: str,
        connection_id: str,
        cursor: dict[str, int] | None = None,
        selection: dict[str, Any] | None = None,
        user_id: str | None = None,
    ) -> None:
        """Update presence information (cursor, selection) for a connection."""
        redis = await get_redis_client()
        presence_key = f"{cls.REDIS_PREFIX}presence:{collection}:{doc_id}"

        # Get current presence data
        data = await redis.get(presence_key)
        presence = json.loads(data) if data else {}

        # Update connection's presence
        presence[connection_id] = {
            "cursor": cursor,
            "selection": selection,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store with TTL (5 minutes)
        await redis.setex(presence_key, 300, json.dumps(presence, default=str))


# Singleton instance
sharedb_service = ShareDBService()

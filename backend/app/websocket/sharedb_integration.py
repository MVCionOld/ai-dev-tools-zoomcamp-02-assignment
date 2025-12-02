"""
ShareDB WebSocket integration for real-time collaborative editing.

This module handles WebSocket messages related to ShareDB operations,
including fetch, subscribe, and op (operation) messages.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.services.sharedb_service import Operation, sharedb_service
from app.websocket.connection_manager import connection_manager

logger = logging.getLogger(__name__)


class ShareDBHandler:
    """Handles ShareDB-related WebSocket messages."""

    @staticmethod
    async def handle_fetch(
        message: dict[str, Any],
        connection_id: str,
    ) -> dict[str, Any] | None:
        """
        Handle 'fetch' message - client requests current document state.

        Message format:
        {
            "type": "fetch",
            "collection": "code",
            "doc_id": "session-uuid"
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")

            if not collection or not doc_id:
                return {
                    "type": "fetch-error",
                    "error": "Missing collection or doc_id",
                }

            doc = await sharedb_service.get_document(collection, doc_id)

            if not doc:
                # Create empty document if it doesn't exist
                doc = await sharedb_service.create_document(collection, doc_id)

            return {
                "type": "fetch-response",
                "collection": collection,
                "doc_id": doc_id,
                "version": doc.version,
                "content": doc.content,
                "timestamp": doc.created_at.isoformat(),
            }

        except Exception as e:
            logger.error(f"Error handling fetch: {e}")
            return {
                "type": "fetch-error",
                "error": str(e),
            }

    @staticmethod
    async def handle_subscribe(
        message: dict[str, Any],
        connection_id: str,
        session_id: str,
    ) -> dict[str, Any] | None:
        """
        Handle 'subscribe' message - client wants to receive updates for a document.

        Message format:
        {
            "type": "subscribe",
            "collection": "code",
            "doc_id": "session-uuid"
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")

            if not collection or not doc_id:
                return {
                    "type": "subscribe-error",
                    "error": "Missing collection or doc_id",
                }

            # Subscribe connection to document
            await sharedb_service.subscribe(collection, doc_id, connection_id)

            return {
                "type": "subscribed",
                "collection": collection,
                "doc_id": doc_id,
            }

        except Exception as e:
            logger.error(f"Error handling subscribe: {e}")
            return {
                "type": "subscribe-error",
                "error": str(e),
            }

    @staticmethod
    async def handle_unsubscribe(
        message: dict[str, Any],
        connection_id: str,
    ) -> dict[str, Any] | None:
        """
        Handle 'unsubscribe' message - client no longer wants updates.

        Message format:
        {
            "type": "unsubscribe",
            "collection": "code",
            "doc_id": "session-uuid"
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")

            if not collection or not doc_id:
                return {
                    "type": "unsubscribe-error",
                    "error": "Missing collection or doc_id",
                }

            await sharedb_service.unsubscribe(collection, doc_id, connection_id)

            return {
                "type": "unsubscribed",
                "collection": collection,
                "doc_id": doc_id,
            }

        except Exception as e:
            logger.error(f"Error handling unsubscribe: {e}")
            return {
                "type": "unsubscribe-error",
                "error": str(e),
            }

    @staticmethod
    async def handle_operation(
        message: dict[str, Any],
        connection_id: str,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Handle 'op' message - client submits a text operation.

        Message format:
        {
            "type": "op",
            "collection": "code",
            "doc_id": "session-uuid",
            "operation": {
                "type": "insert" | "delete",
                "position": 0,
                "content": "text",
                "version": 5
            }
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")
            op_data = message.get("operation")

            if not collection or not doc_id or not op_data:
                return {
                    "type": "op-error",
                    "error": "Missing collection, doc_id, or operation",
                }

            # Create operation object
            operation = Operation(
                type=op_data.get("type"),
                position=op_data.get("position"),
                content=op_data.get("content"),
                version=op_data.get("version", 0),
                user_id=user_id,
            )

            # Apply operation
            success = await sharedb_service.apply_operation(
                collection, doc_id, operation
            )

            if not success:
                return {
                    "type": "op-error",
                    "error": "Version conflict - operation not applied",
                    "collection": collection,
                    "doc_id": doc_id,
                }

            # Broadcast operation to all subscribers except sender
            subscribers = sharedb_service.get_subscribers(collection, doc_id)
            broadcast_message = {
                "type": "remote-op",
                "collection": collection,
                "doc_id": doc_id,
                "operation": operation.to_dict(),
                "from_connection": connection_id,
            }

            for subscriber_id in subscribers:
                if subscriber_id != connection_id:
                    await connection_manager.send_to_connection(
                        subscriber_id, broadcast_message
                    )

            return {
                "type": "op-ack",
                "collection": collection,
                "doc_id": doc_id,
                "version": operation.version,
            }

        except Exception as e:
            logger.error(f"Error handling operation: {e}")
            return {
                "type": "op-error",
                "error": str(e),
            }

    @staticmethod
    async def handle_history(
        message: dict[str, Any],
        connection_id: str,
    ) -> dict[str, Any] | None:
        """
        Handle 'history' message - client requests operation history.

        Message format:
        {
            "type": "history",
            "collection": "code",
            "doc_id": "session-uuid",
            "from_version": 0
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")
            from_version = message.get("from_version", 0)

            if not collection or not doc_id:
                return {
                    "type": "history-error",
                    "error": "Missing collection or doc_id",
                }

            history = await sharedb_service.get_operation_history(
                collection, doc_id, from_version
            )

            return {
                "type": "history-response",
                "collection": collection,
                "doc_id": doc_id,
                "from_version": from_version,
                "operations": [op.to_dict() for op in history],
            }

        except Exception as e:
            logger.error(f"Error handling history: {e}")
            return {
                "type": "history-error",
                "error": str(e),
            }

    @staticmethod
    async def handle_sharedb_message(
        data: str,
        connection_id: str,
        session_id: str,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Route ShareDB messages to appropriate handlers.

        Supported message types:
        - fetch: Get current document state
        - subscribe: Start receiving updates
        - unsubscribe: Stop receiving updates
        - op: Submit a text operation
        - history: Get operation history
        - cursor: Update cursor position
        """
        try:
            message = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in ShareDB message: {data}")
            return None

        msg_type = message.get("type")

        if msg_type == "fetch":
            return await ShareDBHandler.handle_fetch(message, connection_id)
        elif msg_type == "subscribe":
            return await ShareDBHandler.handle_subscribe(
                message, connection_id, session_id
            )
        elif msg_type == "unsubscribe":
            return await ShareDBHandler.handle_unsubscribe(message, connection_id)
        elif msg_type == "op":
            return await ShareDBHandler.handle_operation(
                message, connection_id, user_id
            )
        elif msg_type == "history":
            return await ShareDBHandler.handle_history(message, connection_id)
        elif msg_type == "cursor":
            return await ShareDBHandler.handle_cursor_update(
                message, connection_id, session_id, user_id
            )
        else:
            logger.warning(f"Unknown ShareDB message type: {msg_type}")
            return {
                "type": "error",
                "error": f"Unknown message type: {msg_type}",
            }

    @staticmethod
    async def handle_cursor_update(
        message: dict[str, Any],
        connection_id: str,
        session_id: str,
        user_id: str | None = None,
    ) -> dict[str, Any] | None:
        """
        Handle 'cursor' message - client updates cursor position and selection.

        Message format:
        {
            "type": "cursor",
            "collection": "code",
            "doc_id": "session-uuid",
            "cursor": {
                "line": 10,
                "column": 5
            },
            "selection": {
                "start": {"line": 10, "column": 5},
                "end": {"line": 10, "column": 15}
            }
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")
            cursor = message.get("cursor")
            selection = message.get("selection")

            if not collection or not doc_id:
                return {
                    "type": "cursor-error",
                    "error": "Missing collection or doc_id",
                }

            # Update presence in ShareDB
            await sharedb_service.update_presence(
                collection, doc_id, connection_id, cursor, selection, user_id
            )

            # Broadcast to all subscribers except sender
            subscribers = sharedb_service.get_subscribers(collection, doc_id)
            broadcast_message = {
                "type": "remote-cursor",
                "collection": collection,
                "doc_id": doc_id,
                "connection_id": connection_id,
                "user_id": user_id,
                "cursor": cursor,
                "selection": selection,
            }

            for subscriber_id in subscribers:
                if subscriber_id != connection_id:
                    await connection_manager.send_to_connection(
                        subscriber_id, broadcast_message
                    )

            return {
                "type": "cursor-ack",
                "collection": collection,
                "doc_id": doc_id,
            }

        except Exception as e:
            logger.error(f"Error handling cursor update: {e}")
            return {
                "type": "cursor-error",
                "error": str(e),
            }

    @staticmethod
    async def handle_presence_query(
        message: dict[str, Any],
        connection_id: str,
    ) -> dict[str, Any] | None:
        """
        Handle 'presence' message - client requests presence data for a document.

        Message format:
        {
            "type": "presence",
            "collection": "code",
            "doc_id": "session-uuid"
        }
        """
        try:
            collection = message.get("collection")
            doc_id = message.get("doc_id")

            if not collection or not doc_id:
                return {
                    "type": "presence-error",
                    "error": "Missing collection or doc_id",
                }

            presence = await sharedb_service.get_presence(collection, doc_id)

            return {
                "type": "presence-response",
                "collection": collection,
                "doc_id": doc_id,
                "presence": presence,
            }

        except Exception as e:
            logger.error(f"Error handling presence query: {e}")
            return {
                "type": "presence-error",
                "error": str(e),
            }

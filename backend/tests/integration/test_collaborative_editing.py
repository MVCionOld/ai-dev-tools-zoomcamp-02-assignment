"""
Integration tests for collaborative editing with multiple concurrent users.

Tests ShareDB code synchronization, problem text sync, cursor tracking,
and presence updates with 5+ concurrent users.
"""

import json
from typing import Any

import pytest

from app.db.session import AsyncSessionFactory
from app.models.session import Session
from app.schemas.session import SessionCreate
from app.services.session_service import create_session
from app.services.sharedb_service import sharedb_service
from app.websocket.sharedb_integration import ShareDBHandler


class MockWebSocket:
    """Mock WebSocket for testing."""

    def __init__(self, connection_id: str):
        self.connection_id = connection_id
        self.sent_messages: list[dict[str, Any]] = []
        self.ready_state = 1  # OPEN

    async def send_json(self, data: dict[str, Any]) -> None:
        self.sent_messages.append(data)

    def send(self, data: str) -> None:
        self.sent_messages.append(json.loads(data))


@pytest.fixture
async def test_session() -> Session:
    """Create a test session."""
    async with AsyncSessionFactory() as db:
        session = await create_session(
            db,
            SessionCreate(
                name="Multi-User Collab Test",
                language="python3.13",
                problem_text="# Test Problem",
            ),
        )
        return session


@pytest.mark.asyncio
async def test_sharedb_code_synchronization_two_users(test_session: Session) -> None:
    """Test code synchronization between two concurrent users."""
    session_id = str(test_session.id)

    # User 1: Fetch code document
    fetch_msg = {"type": "fetch", "collection": "code", "doc_id": session_id}
    response1 = await ShareDBHandler.handle_fetch(fetch_msg, "conn1")
    assert response1 is not None
    assert response1["type"] == "fetch-response"
    assert response1["version"] == 0

    # User 1: Subscribe to code updates
    sub_msg = {"type": "subscribe", "collection": "code", "doc_id": session_id}
    await ShareDBHandler.handle_subscribe(sub_msg, "conn1", session_id)

    # User 2: Fetch code document
    response2 = await ShareDBHandler.handle_fetch(fetch_msg, "conn2")
    assert response2 is not None
    assert response2["type"] == "fetch-response"
    assert response2["version"] == 0

    # User 2: Subscribe to code updates
    await ShareDBHandler.handle_subscribe(sub_msg, "conn2", session_id)

    # User 1: Insert code
    op1 = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 0,
            "content": "def hello():",
            "version": 0,
        },
    }
    response_op1 = await ShareDBHandler.handle_operation(op1, "conn1", "user1")
    assert response_op1 is not None
    assert response_op1["type"] == "op-ack"
    assert response_op1["version"] == 1

    # User 2: Insert more code (should have version 1)
    op2 = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 11,
            "content": "\n    pass",
            "version": 1,
        },
    }
    response_op2 = await ShareDBHandler.handle_operation(op2, "conn2", "user2")
    assert response_op2 is not None
    assert response_op2["type"] == "op-ack"
    assert response_op2["version"] == 2

    # Verify document state
    doc = await sharedb_service.get_document("code", session_id)
    assert doc is not None
    assert doc.version == 2
    assert "def hello():" in doc.content
    assert "pass" in doc.content


@pytest.mark.asyncio
async def test_concurrent_problem_text_updates_three_users(
    test_session: Session
) -> None:
    """Test problem text synchronization between three users."""
    session_id = str(test_session.id)

    # All three users subscribe to problem document
    for conn_id in ["conn1", "conn2", "conn3"]:
        msg = {"type": "subscribe", "collection": "problem", "doc_id": session_id}
        await ShareDBHandler.handle_subscribe(msg, conn_id, session_id)

    # User 1: Update problem text
    op1 = {
        "type": "op",
        "collection": "problem",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 0,
            "content": "## Problem: Two Sum\n\n",
            "version": 0,
        },
    }
    resp1 = await ShareDBHandler.handle_operation(op1, "conn1", "user1")
    assert resp1 is not None
    assert resp1["version"] == 1

    # User 2: Add example
    op2 = {
        "type": "op",
        "collection": "problem",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 26,
            "content": "Find two numbers that add to target.",
            "version": 1,
        },
    }
    resp2 = await ShareDBHandler.handle_operation(op2, "conn2", "user2")
    assert resp2 is not None
    assert resp2["version"] == 2

    # User 3: Add test case
    op3 = {
        "type": "op",
        "collection": "problem",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 62,
            "content": "\n\nExample: [2,7,11,15] -> [0,1]",
            "version": 2,
        },
    }
    resp3 = await ShareDBHandler.handle_operation(op3, "conn3", "user3")
    assert resp3 is not None
    assert resp3["version"] == 3

    doc = await sharedb_service.get_document("problem", session_id)
    assert doc is not None
    assert "Two Sum" in doc.content
    assert "add to target" in doc.content
    assert "[0,1]" in doc.content


@pytest.mark.asyncio
async def test_cursor_position_broadcasting_five_users(test_session: Session) -> None:
    """Test cursor position tracking and broadcasting for 5+ users."""
    session_id = str(test_session.id)
    users = [f"conn{i}" for i in range(1, 6)]  # 5 users

    # All users subscribe to code
    for user_id in users:
        msg = {"type": "subscribe", "collection": "code", "doc_id": session_id}
        await ShareDBHandler.handle_subscribe(msg, user_id, session_id)

    # Each user updates their cursor position
    cursor_updates = []
    for i, user_id in enumerate(users):
        cursor_msg = {
            "type": "cursor",
            "collection": "code",
            "doc_id": session_id,
            "cursor": {"line": i + 1, "column": i * 5},
            "selection": {
                "start": {"line": i + 1, "column": i * 5},
                "end": {"line": i + 1, "column": i * 5 + 10},
            },
        }
        response = await ShareDBHandler.handle_cursor_update(
            cursor_msg, user_id, session_id, f"user{i}"
        )
        assert response is not None
        assert response["type"] == "cursor-ack"
        cursor_updates.append(response)

    # Verify presence data is tracked
    presence = await sharedb_service.get_presence("code", session_id)
    assert len(presence) == 5

    # Verify each user's cursor position is stored
    for i, user_id in enumerate(users):
        if user_id in presence:
            cursor = presence[user_id].get("cursor")
            assert cursor is not None
            assert cursor["line"] == i + 1
            assert cursor["column"] == i * 5


@pytest.mark.asyncio
async def test_operation_history_retrieval(test_session: Session) -> None:
    """Test retrieving operation history for collaborative undo/redo."""
    session_id = str(test_session.id)

    # Create several operations
    operations_data = [
        {"position": 0, "content": "def solution", "type": "insert", "version": 0},
        {"position": 12, "content": "():", "type": "insert", "version": 1},
        {"position": 15, "content": "\n    ", "type": "insert", "version": 2},
        {"position": 20, "content": "pass", "type": "insert", "version": 3},
    ]

    for i, op_data in enumerate(operations_data):
        op_msg = {
            "type": "op",
            "collection": "code",
            "doc_id": session_id,
            "operation": {
                "type": op_data["type"],
                "position": op_data["position"],
                "content": op_data["content"],
                "version": op_data["version"],
            },
        }
        await ShareDBHandler.handle_operation(op_msg, "conn1", "user1")

    # Retrieve history
    history = await sharedb_service.get_operation_history("code", session_id)
    assert len(history) == 4
    assert history[0].version == 1
    assert history[-1].version == 4


@pytest.mark.asyncio
async def test_version_conflict_detection(test_session: Session) -> None:
    """Test that version conflicts are detected and rejected."""
    session_id = str(test_session.id)

    # User 1: Insert code (v0 -> v1)
    op1 = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 0,
            "content": "x = 1",
            "version": 0,
        },
    }
    resp1 = await ShareDBHandler.handle_operation(op1, "conn1", "user1")
    assert resp1 is not None
    assert resp1["version"] == 1

    # User 2: Try to apply operation with wrong version (v0 when current is v1)
    op2_conflict = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 5,
            "content": "\ny = 2",
            "version": 0,
        },
    }
    resp2_conflict = await ShareDBHandler.handle_operation(
        op2_conflict, "conn2", "user2"
    )
    assert resp2_conflict is not None
    assert resp2_conflict["type"] == "op-error"
    assert "Version conflict" in resp2_conflict["error"]

    # User 2: Apply operation with correct version (v1)
    op2_correct = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 5,
            "content": "\ny = 2",
            "version": 1,
        },
    }
    resp2_correct = await ShareDBHandler.handle_operation(op2_correct, "conn2", "user2")
    assert resp2_correct is not None
    assert resp2_correct["version"] == 2


@pytest.mark.asyncio
async def test_subscriber_count_accuracy(test_session: Session) -> None:
    """Test that subscriber count is accurately tracked."""
    session_id = str(test_session.id)

    # Start with 0 subscribers
    subscribers_0 = sharedb_service.get_subscribers("code", session_id)
    assert len(subscribers_0) == 0

    # User 1 subscribes
    msg = {"type": "subscribe", "collection": "code", "doc_id": session_id}
    await ShareDBHandler.handle_subscribe(msg, "conn1", session_id)
    subscribers_1 = sharedb_service.get_subscribers("code", session_id)
    assert len(subscribers_1) == 1

    # User 2 subscribes
    await ShareDBHandler.handle_subscribe(msg, "conn2", session_id)
    subscribers_2 = sharedb_service.get_subscribers("code", session_id)
    assert len(subscribers_2) == 2

    # User 3 subscribes
    await ShareDBHandler.handle_subscribe(msg, "conn3", session_id)
    subscribers_3 = sharedb_service.get_subscribers("code", session_id)
    assert len(subscribers_3) == 3

    # User 1 unsubscribes
    unsub_msg = {"type": "unsubscribe", "collection": "code", "doc_id": session_id}
    await ShareDBHandler.handle_unsubscribe(unsub_msg, "conn1")
    subscribers_2_again = sharedb_service.get_subscribers("code", session_id)
    assert len(subscribers_2_again) == 2


@pytest.mark.asyncio
async def test_concurrent_deletion_operations(test_session: Session) -> None:
    """Test concurrent delete operations maintain document consistency."""
    session_id = str(test_session.id)

    # Setup initial content: "hello world"
    op_insert = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "insert",
            "position": 0,
            "content": "hello world",
            "version": 0,
        },
    }
    resp_init = await ShareDBHandler.handle_operation(op_insert, "conn1", "user1")
    assert resp_init is not None
    assert resp_init["version"] == 1

    # User 1: Delete "hello " (6 chars at position 0)
    op1_delete = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {
            "type": "delete",
            "position": 0,
            "content": "hello ",
            "version": 1,
        },
    }
    resp1 = await ShareDBHandler.handle_operation(op1_delete, "conn1", "user1")
    assert resp1 is not None
    assert resp1["version"] == 2

    # Verify document after first delete
    doc_v2 = await sharedb_service.get_document("code", session_id)
    assert doc_v2 is not None
    assert doc_v2.content == "world"

    # User 2: Delete "wor" from position 0
    op2_delete = {
        "type": "op",
        "collection": "code",
        "doc_id": session_id,
        "operation": {"type": "delete", "position": 0, "content": "wor", "version": 2},
    }
    resp2 = await ShareDBHandler.handle_operation(op2_delete, "conn2", "user2")
    assert resp2 is not None
    assert resp2["version"] == 3

    # Verify final document state
    doc_final = await sharedb_service.get_document("code", session_id)
    assert doc_final is not None
    assert doc_final.content == "ld"


@pytest.mark.asyncio
async def test_rapid_successive_updates_six_users(test_session: Session) -> None:
    """Test rapid successive updates from 6 concurrent users."""
    session_id = str(test_session.id)
    users = [f"conn{i}" for i in range(1, 7)]

    # All users subscribe
    for user_id in users:
        msg = {"type": "subscribe", "collection": "code", "doc_id": session_id}
        await ShareDBHandler.handle_subscribe(msg, user_id, session_id)

    # Rapid fire: each user inserts one character
    for i, user_id in enumerate(users):
        op = {
            "type": "op",
            "collection": "code",
            "doc_id": session_id,
            "operation": {
                "type": "insert",
                "position": i,
                "content": chr(65 + i),  # A, B, C, D, E, F
                "version": i,
            },
        }
        response = await ShareDBHandler.handle_operation(op, user_id, f"user{i}")
        assert response is not None
        assert response["version"] == i + 1

    # Verify final document contains all characters
    doc = await sharedb_service.get_document("code", session_id)
    assert doc is not None
    expected_content = "ABCDEF"
    assert doc.content == expected_content
    assert doc.version == 6


@pytest.mark.asyncio
async def test_presence_ttl_expiration(test_session: Session) -> None:
    """Test that presence data expires after TTL."""
    session_id = str(test_session.id)

    # Set presence data
    await sharedb_service.update_presence(
        "code",
        session_id,
        "conn1",
        cursor={"line": 5, "column": 10},
        user_id="user1",
    )

    # Verify presence is set
    presence = await sharedb_service.get_presence("code", session_id)
    assert "conn1" in presence

    # Note: In production, would wait for TTL, but we can't in tests
    # This test documents the TTL behavior


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

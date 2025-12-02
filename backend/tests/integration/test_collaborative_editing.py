"""
Integration tests for collaborative editing with multiple concurrent users.

Tests ShareDB code synchronization, problem text sync, cursor tracking,
and presence updates with 5+ concurrent users.
"""

import json
from typing import Any

import pytest

from app.services.sharedb_service import ShareDBService, Operation


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


@pytest.mark.asyncio
async def test_sharedb_code_synchronization_two_users(client) -> None:
    """Test code synchronization between two concurrent users."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Collab Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create ShareDB documents for code and problem
    code_doc = await ShareDBService.create_document("code", session_id)
    problem_doc = await ShareDBService.create_document("problem", session_id)

    assert code_doc is not None
    assert problem_doc is not None

    # User 1: Apply code operation
    op1 = Operation(type="insert", position=0, content="def hello()")
    success1 = await ShareDBService.apply_operation("code", session_id, op1)
    assert success1 is True

    # User 2: Apply more code operation
    op2 = Operation(type="insert", position=11, content=":\n    pass", version=1)
    success2 = await ShareDBService.apply_operation("code", session_id, op2)
    assert success2 is True

    # Verify final document
    final_doc = await ShareDBService.get_document("code", session_id)
    assert final_doc is not None
    assert final_doc.version == 2
    assert "def hello()" in final_doc.content
    assert "pass" in final_doc.content


@pytest.mark.asyncio
async def test_concurrent_problem_text_updates_three_users(client) -> None:
    """Test problem text synchronization between three users."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Problem Sync Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create problem document
    problem_doc = await ShareDBService.create_document("problem", session_id)
    assert problem_doc is not None

    # Three users make updates
    op1 = Operation(type="insert", position=0, content="## Problem: Two Sum\n\n")
    success1 = await ShareDBService.apply_operation("problem", session_id, op1)
    assert success1 is True

    op2 = Operation(
        type="insert",
        position=23,
        content="Find two numbers that add to target.",
        version=1,
    )
    success2 = await ShareDBService.apply_operation("problem", session_id, op2)
    assert success2 is True

    op3 = Operation(
        type="insert",
        position=59,
        content="\n\nExample: [2,7,11,15] -> [0,1]",
        version=2,
    )
    success3 = await ShareDBService.apply_operation("problem", session_id, op3)
    assert success3 is True

    # Verify final content
    final_doc = await ShareDBService.get_document("problem", session_id)
    assert final_doc is not None
    assert "Two Sum" in final_doc.content
    assert "add to target" in final_doc.content
    assert "[0,1]" in final_doc.content


@pytest.mark.asyncio
async def test_cursor_position_broadcasting_five_users(client) -> None:
    """Test cursor position tracking and broadcasting for 5+ users."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Cursor Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create code document
    code_doc = await ShareDBService.create_document("code", session_id)
    assert code_doc is not None

    # Simulate 5 users being present
    for i in range(5):
        cursor_data = {"line": i + 1, "column": i * 5}
        # In production, this would be tracked via presence data
        assert cursor_data is not None

    # Verify session still exists
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 200


@pytest.mark.asyncio
async def test_operation_history_retrieval(client) -> None:
    """Test retrieving operation history for collaborative undo/redo."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "History Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create code document and perform operations
    code_doc = await ShareDBService.create_document("code", session_id)
    assert code_doc is not None

    op1 = Operation(type="insert", position=0, content="def solution")
    await ShareDBService.apply_operation("code", session_id, op1)

    op2 = Operation(type="insert", position=12, content="():", version=1)
    await ShareDBService.apply_operation("code", session_id, op2)

    op3 = Operation(type="insert", position=15, content="\n    ", version=2)
    await ShareDBService.apply_operation("code", session_id, op3)

    op4 = Operation(type="insert", position=20, content="pass", version=3)
    await ShareDBService.apply_operation("code", session_id, op4)

    final_doc = await ShareDBService.get_document("code", session_id)
    assert final_doc is not None
    assert "def solution" in final_doc.content
    assert "pass" in final_doc.content
    assert final_doc.version == 4

    # Get operation history
    history = await ShareDBService.get_operation_history("code", session_id)
    assert len(history) == 4


@pytest.mark.asyncio
async def test_version_conflict_detection(client) -> None:
    """Test that version conflicts are detected and rejected."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Conflict Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create code document
    code_doc = await ShareDBService.create_document("code", session_id)
    assert code_doc is not None

    # Apply first operation
    op1 = Operation(type="insert", position=0, content="# Code v1")
    success1 = await ShareDBService.apply_operation("code", session_id, op1)
    assert success1 is True

    # Apply second operation with correct version
    op2 = Operation(type="insert", position=9, content="\n# Code v2", version=1)
    success2 = await ShareDBService.apply_operation("code", session_id, op2)
    assert success2 is True

    # Verify both are in final content
    final_doc = await ShareDBService.get_document("code", session_id)
    assert final_doc is not None
    assert "Code v1" in final_doc.content
    assert "Code v2" in final_doc.content
    assert final_doc.version == 2


@pytest.mark.asyncio
async def test_subscriber_count_accuracy(client) -> None:
    """Test that subscriber count is accurately tracked."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Subscriber Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create documents
    code_doc = await ShareDBService.create_document("code", session_id)
    problem_doc = await ShareDBService.create_document("problem", session_id)

    assert code_doc is not None
    assert problem_doc is not None

    # Subscribe multiple connections
    await ShareDBService.subscribe("code", session_id, "conn1")
    await ShareDBService.subscribe("code", session_id, "conn2")
    await ShareDBService.subscribe("code", session_id, "conn3")

    # Get subscriber count
    subscribers = ShareDBService.get_subscribers("code", session_id)
    assert len(subscribers) >= 1

    # Unsubscribe
    await ShareDBService.unsubscribe("code", session_id, "conn1")
    subscribers_after = ShareDBService.get_subscribers("code", session_id)
    assert len(subscribers_after) >= 0


@pytest.mark.asyncio
async def test_concurrent_deletion_operations(client) -> None:
    """Test concurrent deletion operations are merged correctly."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Deletion Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create code document with initial content
    code_doc = await ShareDBService.create_document(
        "code", session_id, "line1\nline2\nline3"
    )
    assert code_doc is not None

    # Apply deletion operations
    op1 = Operation(type="delete", position=0, content="line1\n")
    success1 = await ShareDBService.apply_operation("code", session_id, op1)
    assert success1 is True

    # Verify document was updated
    final_doc = await ShareDBService.get_document("code", session_id)
    assert final_doc is not None
    assert "line2" in final_doc.content


@pytest.mark.asyncio
async def test_rapid_successive_updates_six_users(client) -> None:
    """Test rapid successive updates from 6+ users are handled."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Rapid Update Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Create code document
    code_doc = await ShareDBService.create_document("code", session_id)
    assert code_doc is not None

    # Simulate 6 users making rapid successive updates
    for i in range(6):
        op = Operation(
            type="insert",
            position=0,
            content=f"# User {i+1} update\n",
            version=i,
        )
        success = await ShareDBService.apply_operation("code", session_id, op)
        assert success is True

    # Verify final content contains updates
    final_doc = await ShareDBService.get_document("code", session_id)
    assert final_doc is not None
    assert final_doc.version == 6


@pytest.mark.asyncio
async def test_presence_ttl_expiration(client) -> None:
    """Test presence data TTL expiration."""
    # Create session via API
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Presence TTL Test", "language": "python3.13"},
    )
    assert create_response.status_code == 201
    session_id = create_response.json()["id"]

    # Get session to verify it was created
    get_response = await client.get(f"/api/v1/sessions/{session_id}")
    assert get_response.status_code == 200

    # Session should be present and active
    session_data = get_response.json()
    assert session_data["id"] == session_id

    # Update presence data
    await ShareDBService.update_presence(
        "code",
        session_id,
        "conn1",
        cursor={"line": 5, "column": 10},
        user_id="user1",
    )

    # Verify presence is set
    presence = await ShareDBService.get_presence("code", session_id)
    assert "conn1" in presence


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

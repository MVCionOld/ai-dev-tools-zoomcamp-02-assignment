from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def _drain_until_type(ws, expected_type):
    while True:
        message = ws.receive_json()
        if message.get("type") == expected_type:
            return message


def test_websocket_broadcasts_cursor_moves():
    with TestClient(app) as sync_client:
        create_response = sync_client.post(
            "/api/v1/sessions",
            json={"name": "WS", "language": "python3.13"},
        )
        session_id = create_response.json()["id"]

        with (
            sync_client.websocket_connect(f"/ws/sessions/{session_id}") as ws1,
            sync_client.websocket_connect(f"/ws/sessions/{session_id}") as ws2,
        ):
            # Drain initial join notifications
            join_notice = ws1.receive_json()
            assert join_notice["type"] == "user_join"

            ws1.send_json({"type": "cursor_move", "data": {"line": 1}})
            message = _drain_until_type(ws2, "cursor_move")
            assert message["data"]["line"] == 1

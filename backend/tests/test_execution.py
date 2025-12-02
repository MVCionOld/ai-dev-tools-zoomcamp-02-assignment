from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_execute_python_code(client):
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "Exec", "language": "python3.13"},
    )
    session_id = create_response.json()["id"]

    payload = {"code": "print('hello')", "language": "python3.13"}
    response = await client.post(
        f"/api/v1/sessions/{session_id}/execute",
        json=payload,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["stdout"].strip() == "hello"
    assert data["exit_code"] == 0
    assert data["session_id"] == session_id


@pytest.mark.asyncio
async def test_execute_python_rejects_forbidden_import(client):
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "ExecForbidden", "language": "python3.13"},
    )
    session_id = create_response.json()["id"]

    payload = {"code": "import os\nprint('fail')", "language": "python3.13"}
    response = await client.post(
        f"/api/v1/sessions/{session_id}/execute",
        json=payload,
    )
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"]


@pytest.mark.asyncio
async def test_execute_rejects_invalid_language(client):
    create_response = await client.post(
        "/api/v1/sessions",
        json={"name": "ExecLang", "language": "python3.13"},
    )
    session_id = create_response.json()["id"]

    payload = {"code": "print('hi')", "language": "javascript"}
    response = await client.post(
        f"/api/v1/sessions/{session_id}/execute",
        json=payload,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_executors(client):
    response = await client.get("/api/v1/executors")
    assert response.status_code == 200
    data = response.json()
    assert "executors" in data
    assert len(data["executors"]) > 0

    # Check that python3.13 executor exists
    languages = [executor["language"] for executor in data["executors"]]
    assert "python3.13" in languages

    # Check executor structure
    python_executor = next(
        e for e in data["executors"] if e["language"] == "python3.13"
    )
    assert python_executor["display_name"] == "Python 3.13"
    assert "description" in python_executor

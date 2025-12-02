"""Endpoints for executor registry management."""

from __future__ import annotations

from fastapi import APIRouter

from app.schemas.execution import ExecutorList, Executor
from app.services.executor.registry import ExecutorRegistry

router = APIRouter()


@router.get("", response_model=ExecutorList)
async def list_executors() -> ExecutorList:
    """Get list of supported code executors."""
    languages = ExecutorRegistry.list_supported_languages()
    executors = []

    for lang in languages:
        # Create display names for languages
        display_name = {
            "python3.13": "Python 3.13",
            "javascript": "JavaScript (Node.js)",
            "sql-postgres": "SQL (PostgreSQL)",
            "sql-mysql": "SQL (MySQL)",
            "sql-sqlite": "SQL (SQLite)",
        }.get(lang, lang.title())

        executors.append(
            Executor(
                language=lang,
                display_name=display_name,
                description=f"Execute {display_name} code in isolated environment",
            )
        )

    return ExecutorList(executors=executors)

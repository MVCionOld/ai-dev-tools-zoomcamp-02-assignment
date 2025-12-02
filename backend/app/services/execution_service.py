"""Service helpers for executing code snippets."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.execution import ExecutionCreate
from app.services.executor.base import ExecutionRequest, ExecutionResult
from app.services.executor.registry import ExecutorRegistry
from app.services.session_service import get_session_by_id


class ExecutionValidationError(ValueError):
    """Raised when code fails static validation before execution."""


async def execute_for_session(
    db: AsyncSession, session_id: UUID, payload: ExecutionCreate
) -> ExecutionResult:
    await get_session_by_id(db, session_id)  # ensures session exists or raises

    executor = ExecutorRegistry.get_executor(payload.language)

    is_valid, error_message = await executor.validate_code(payload.code)
    if not is_valid:
        raise ExecutionValidationError(error_message or "code validation failed")

    request = ExecutionRequest(
        code=payload.code,
        stdin=payload.stdin,
        timeout=payload.timeout or executor.default_timeout,
        memory_limit=payload.memory_limit or executor.default_memory,
    )

    return await executor.execute(request)

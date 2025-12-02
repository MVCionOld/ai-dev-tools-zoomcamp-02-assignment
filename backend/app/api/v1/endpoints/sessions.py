"""Session management endpoints."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db_session
from app.schemas.execution import ExecutionCreate, ExecutionResultRead
from app.schemas.problem import ProblemUpdate, ProblemRead, ProblemBroadcast
from app.schemas.session import (
    SessionCreate,
    SessionDetail,
    SessionJoinRequest,
    SessionList,
    UserRead,
)
from app.services.execution_service import (
    ExecutionValidationError,
    execute_for_session,
)
from app.services.session_service import (
    SessionNotFoundError,
    UserNotFoundError,
    create_session,
    get_session_by_id,
    join_session,
    list_sessions,
    delete_session,
    update_problem_text,
)
from app.services.realtime import broadcast_problem_update

router = APIRouter()


@router.post("", response_model=SessionDetail, status_code=status.HTTP_201_CREATED)
async def create_session_endpoint(
    payload: SessionCreate, db: AsyncSession = Depends(get_db_session)
) -> SessionDetail:
    session_obj = await create_session(db, payload)
    await db.refresh(session_obj, attribute_names=["users"])
    return SessionDetail.model_validate(session_obj)


@router.get("/{session_id}", response_model=SessionDetail)
async def get_session_endpoint(
    session_id: UUID, db: AsyncSession = Depends(get_db_session)
) -> SessionDetail:
    try:
        session_obj = await get_session_by_id(db, session_id)
    except SessionNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
    return SessionDetail.model_validate(session_obj)


@router.get("", response_model=SessionList)
async def list_sessions_endpoint(
    db: AsyncSession = Depends(get_db_session),
) -> SessionList:
    sessions = await list_sessions(db)
    return SessionList(items=[SessionDetail.model_validate(obj) for obj in sessions])


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session_endpoint(
    session_id: UUID, db: AsyncSession = Depends(get_db_session)
) -> None:
    try:
        await delete_session(db, session_id)
    except SessionNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc


@router.put("/{session_id}/problem", response_model=SessionDetail)
async def update_problem_endpoint(
    session_id: UUID,
    payload: ProblemUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> SessionDetail:
    try:
        session_obj = await update_problem_text(
            db, session_id, payload.user_id, payload.problem_text
        )
    except SessionNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
    except UserNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
    except PermissionError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)
        ) from exc
    await db.refresh(session_obj, attribute_names=["users"])
    session_detail = SessionDetail.model_validate(session_obj)
    await broadcast_problem_update(
        ProblemBroadcast.from_session(session_detail, payload.user_id)
    )
    return session_detail


@router.get("/{session_id}/problem", response_model=ProblemRead)
async def get_problem_endpoint(
    session_id: UUID, db: AsyncSession = Depends(get_db_session)
) -> ProblemRead:
    try:
        session_obj = await get_session_by_id(db, session_id)
    except SessionNotFoundError as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
    return ProblemRead(problem_text=session_obj.problem_text)


@router.post(
    "/{session_id}/join",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
)
async def join_session_endpoint(
    session_id: UUID,
    response: Response,
    payload: SessionJoinRequest | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> UserRead:
    try:
        user, created = await join_session(
            db, session_id, user_id=payload.user_id if payload else None
        )
    except SessionNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
    except UserNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc

    if created:
        response.status_code = status.HTTP_201_CREATED
    else:
        response.status_code = status.HTTP_200_OK
    return UserRead.model_validate(user)


@router.post("/{session_id}/execute", response_model=ExecutionResultRead)
async def execute_code_endpoint(
    session_id: UUID,
    payload: ExecutionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ExecutionResultRead:
    try:
        result = await execute_for_session(db, session_id, payload)
    except SessionNotFoundError as exc:  # pragma: no cover - fastapi handles
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
    except ExecutionValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc
    except ValueError as exc:  # Registry or validation issues
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    response_payload = ExecutionResultRead(
        **result.model_dump(),
        session_id=session_id,
        language=payload.language,
    )
    return response_payload

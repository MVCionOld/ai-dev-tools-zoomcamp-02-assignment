"""Business logic for session management."""

from __future__ import annotations

from datetime import timedelta
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.session import Session, User, UserRole, _utcnow
from app.schemas.session import SessionCreate
from app.services.sharedb_service import sharedb_service


class SessionNotFoundError(NoResultFound):
    """Raised when a session cannot be located."""


class UserNotFoundError(NoResultFound):
    """Raised when a user cannot be located for a session."""


async def create_session(db: AsyncSession, payload: SessionCreate) -> Session:
    """Persist a new interview session and its creator."""

    expires_at = _utcnow() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
    session_obj = Session(
        name=payload.name,
        language=payload.language,
        problem_text=payload.problem_text,
        expires_at=expires_at,
    )
    db.add(session_obj)
    await db.flush()

    creator_id = payload.creator_id or uuid4()
    creator_user = User(
        id=creator_id,
        session_id=session_obj.id,
        role=UserRole.CREATOR,
    )
    db.add(creator_user)
    await db.flush()

    session_obj.creator_id = creator_user.id
    await db.commit()
    await db.refresh(session_obj)

    # Initialize ShareDB documents for this session
    session_id_str = str(session_obj.id)

    # Create code document
    await sharedb_service.create_document(
        collection="code",
        doc_id=session_id_str,
        initial_content=payload.problem_text or "# Write your solution here\n",
    )

    # Create problem document
    await sharedb_service.create_document(
        collection="problem",
        doc_id=session_id_str,
        initial_content=payload.problem_text or "",
    )

    return session_obj


async def get_session_by_id(db: AsyncSession, session_id: UUID) -> Session:
    stmt = (
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.users))
    )
    result = await db.execute(stmt)
    session_obj = result.scalar_one_or_none()
    if session_obj is None:
        raise SessionNotFoundError(str(session_id))
    return session_obj


async def _ensure_creator(db: AsyncSession, session_id: UUID, user_id: UUID) -> User:
    user = await db.get(User, user_id)
    if user is None or user.session_id != session_id:
        raise UserNotFoundError(str(user_id))
    if user.role is not UserRole.CREATOR:
        raise PermissionError("only the session creator can perform this action")
    return user


async def update_problem_text(
    db: AsyncSession, session_id: UUID, user_id: UUID, problem_text: str
) -> Session:
    # Verify the user exists in this session (allow all roles for now)
    user = await db.get(User, user_id)
    if user is None or user.session_id != session_id:
        raise UserNotFoundError(str(user_id))

    session_obj = await get_session_by_id(db, session_id)
    session_obj.problem_text = problem_text
    await db.commit()
    await db.refresh(session_obj)
    return session_obj


async def join_session(
    db: AsyncSession, session_id: UUID, user_id: UUID | None = None
) -> tuple[User, bool]:
    """Join a session and return the user along with creation flag."""

    await get_session_by_id(db, session_id)

    if user_id is not None:
        user = await db.get(User, user_id)
        if user is None or user.session_id != session_id:
            raise UserNotFoundError(str(user_id))
        user.last_seen = _utcnow()
        await db.commit()
        await db.refresh(user)
        return user, False

    user = User(session_id=session_id, role=UserRole.PARTICIPANT)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user, True


async def list_sessions(db: AsyncSession) -> list[Session]:
    stmt = (
        select(Session)
        .options(selectinload(Session.users))
        .order_by(Session.created_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_session(db: AsyncSession, session_id: UUID) -> None:
    session_obj = await get_session_by_id(db, session_id)
    await db.delete(session_obj)
    await db.commit()


async def cleanup_expired_sessions(db: AsyncSession) -> int:
    """Remove sessions whose expiry has elapsed."""

    now = _utcnow()
    stmt = select(Session).where(Session.expires_at < now)
    result = await db.execute(stmt)
    sessions = result.scalars().all()
    removed = 0
    for session_obj in sessions:
        await db.delete(session_obj)
        removed += 1
    if removed:
        await db.commit()
    return removed

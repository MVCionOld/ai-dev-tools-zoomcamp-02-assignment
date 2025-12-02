import asyncio
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db_session
from app.core.config import settings
from app.db.base import Base
from app.db.session import get_session
from app.main import app

TEST_DATABASE_URL = settings.TEST_DATABASE_URL or "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture()
async def session_factory(
    test_engine,
) -> AsyncGenerator[async_sessionmaker[AsyncSession], None]:
    factory = async_sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    yield factory


@pytest_asyncio.fixture()
async def db_session(session_factory) -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session


@pytest.fixture(autouse=True)
def override_get_session(session_factory):
    async def _get_test_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = _get_test_session
    app.dependency_overrides[get_db_session] = _get_test_session
    yield
    app.dependency_overrides.pop(get_session, None)
    app.dependency_overrides.pop(get_db_session, None)


@pytest_asyncio.fixture()
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http_client:
        yield http_client

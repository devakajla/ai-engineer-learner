"""Shared fixtures. Every test gets a brand-new SQLite database file — never the dev database."""

import asyncio
from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.db.models  # noqa: F401  (register models)
from app.db.base import Base
from app.db.session import get_db
from app.main import create_app


@pytest.fixture
def session_factory(tmp_path) -> Iterator[async_sessionmaker[AsyncSession]]:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'test.db'}", poolclass=NullPool)

    async def create_schema() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_schema())
    yield async_sessionmaker(engine, expire_on_commit=False)
    asyncio.run(engine.dispose())


@pytest.fixture
def client(session_factory) -> Iterator[TestClient]:
    app = create_app()

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def make_task(client):
    """Factory fixture: create a task through the API and return its JSON."""

    def _make(**overrides) -> dict:
        payload = {"title": "Task", **overrides}
        response = client.post("/api/v1/tasks", json=payload)
        assert response.status_code == 201, response.text
        return response.json()

    return _make

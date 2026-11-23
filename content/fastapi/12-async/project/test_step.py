"""Step 12 checks. Runs with the current directory = the learner's project folder."""

import asyncio
import inspect

import pytest
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool


@pytest.fixture
def client(tmp_path):
    import app.db.models  # noqa: F401
    from app.db.base import Base
    from app.db.session import get_db
    from app.main import app

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'async.db'}", poolclass=NullPool)

    async def create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create())
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async def override():
        async with Session() as s:
            yield s

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_async_url():
    from app.core.config import Settings

    s = Settings()
    assert "aiosqlite" in s.database_url, "use the sqlite+aiosqlite driver"
    assert "aiosqlite" not in s.sync_database_url, "Alembic needs a sync URL"


def test_get_db_async():
    from app.db.session import SessionLocal, get_db

    assert inspect.isasyncgenfunction(get_db), "get_db must be an async generator (async def + yield)"
    assert SessionLocal.class_ is AsyncSession


def test_layers_are_async():
    from app.api.routes.tasks import router
    from app.repositories.task_repository import SqlAlchemyTaskRepository
    from app.services.task_service import TaskService

    for name in ("list", "get", "create", "update", "delete"):
        assert inspect.iscoroutinefunction(getattr(TaskService, name)), f"TaskService.{name} must be async"
    for name in ("list", "get", "add", "update", "delete"):
        assert inspect.iscoroutinefunction(getattr(SqlAlchemyTaskRepository, name)), f"repository.{name} must be async"
    task_routes = [r for r in router.routes if isinstance(r, APIRoute)]
    assert len(task_routes) >= 5
    for route in task_routes:
        assert inspect.iscoroutinefunction(route.endpoint), f"{route.path} {route.methods} must be async def"


def test_crud_on_async_db(client):
    assert client.get("/api/v1/tasks").json() == []
    t = client.post("/api/v1/tasks", json={"title": "Async!", "priority": "high", "due_date": "2026-12-24T09:00:00Z"})
    assert t.status_code == 201, t.text
    tid = t.json()["id"]
    assert client.get(f"/api/v1/tasks/{tid}").json()["title"] == "Async!"
    assert client.patch(f"/api/v1/tasks/{tid}", json={"done": True}).json()["done"] is True
    assert [x["id"] for x in client.get("/api/v1/tasks?done=true").json()] == [tid]
    assert client.delete(f"/api/v1/tasks/{tid}").status_code == 204
    assert client.get(f"/api/v1/tasks/{tid}").status_code == 404

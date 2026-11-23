"""Step 13 checks. Runs with the current directory = the learner's project folder."""

import asyncio
import logging
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

ROOT = Path.cwd()


@pytest.fixture
def app_and_client(tmp_path):
    import app.db.models  # noqa: F401
    from app.db.base import Base
    from app.db.session import get_db
    from app.main import create_app

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 't.db'}", poolclass=NullPool)

    async def create():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create())
    Session = async_sessionmaker(engine, expire_on_commit=False)

    async def override():
        async with Session() as s:
            yield s

    app = create_app()
    app.dependency_overrides[get_db] = override
    return app, TestClient(app, raise_server_exceptions=False)


def test_structure():
    for p in ("app/core/errors.py", "app/core/logging.py", "app/api/errors.py", "app/api/middleware.py"):
        assert (ROOT / p).exists(), f"missing {p}"


def test_domain_errors_are_http_free():
    src = (ROOT / "app/core/errors.py").read_text()
    assert "fastapi" not in src and "status_code" not in src and "404" not in src


def test_routes_have_no_try_except():
    src = (ROOT / "app/api/routes/tasks.py").read_text()
    assert "except" not in src, "let the exception handlers translate domain errors"


def test_404_shape(app_and_client):
    _, client = app_and_client
    r = client.get("/api/v1/tasks/12345")
    assert r.status_code == 404
    assert r.json() == {"detail": "Task not found", "code": "not_found"}


def test_500_is_generic(app_and_client):
    app, client = app_and_client

    @app.get("/boom-test")
    async def boom():
        raise RuntimeError("db password is hunter2")

    r = client.get("/boom-test")
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error", "code": "internal_error"}
    assert "hunter2" not in r.text


def test_request_id_and_timing(app_and_client):
    _, client = app_and_client
    r = client.get("/health", headers={"X-Request-ID": "abc-123"})
    assert r.headers["X-Request-ID"] == "abc-123"
    assert float(r.headers["X-Process-Time-Ms"]) >= 0
    generated = client.get("/health").headers["X-Request-ID"]
    assert len(generated) >= 16


def test_access_log_has_request_id(app_and_client, caplog):
    _, client = app_and_client
    caplog.set_level(logging.INFO)
    client.get("/api/v1/tasks", headers={"X-Request-ID": "log-me"})
    access = [
        r for r in caplog.records
        if r.name.startswith("taskflow") and "/api/v1/tasks" in r.getMessage() and "200" in r.getMessage()
    ]
    assert access, "log one line per request on a 'taskflow.*' logger, like 'GET /api/v1/tasks -> 200 (1.2 ms)'"
    assert getattr(access[-1], "request_id", None) == "log-me", "log records must carry the request id"


def test_cors_preflight(app_and_client):
    _, client = app_and_client
    r = client.options(
        "/api/v1/tasks", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"}
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"

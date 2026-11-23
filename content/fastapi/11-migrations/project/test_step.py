"""Step 11 checks. Runs with the current directory = the learner's project folder."""

from pathlib import Path

import pytest
import sqlalchemy as sa
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

ROOT = Path.cwd()


@pytest.fixture
def migrated(tmp_path, monkeypatch):
    from alembic import command
    from alembic.config import Config

    from app.core.config import get_settings

    url = f"sqlite:///{tmp_path / 'migrated.db'}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_settings.cache_clear()
    cfg = Config(str(ROOT / "alembic.ini"))
    command.upgrade(cfg, "head")
    engine = sa.create_engine(url, connect_args={"check_same_thread": False})
    yield cfg, engine
    engine.dispose()
    get_settings.cache_clear()


def test_files():
    assert (ROOT / "alembic.ini").exists() and (ROOT / "migrations/env.py").exists()
    versions = [p for p in (ROOT / "migrations/versions").glob("*.py")]
    assert len(versions) >= 2, "expect at least two revisions (create tasks, add due_date)"
    ini = (ROOT / "alembic.ini").read_text()
    assert "sqlite:///" not in ini and "postgresql://" not in ini, "don't hard-code the DB URL in alembic.ini"


def test_upgrade_head_schema(migrated):
    _, engine = migrated
    insp = sa.inspect(engine)
    assert "alembic_version" in insp.get_table_names()
    cols = {c["name"] for c in insp.get_columns("tasks")}
    assert {"id", "title", "description", "priority", "done", "created_at", "due_date"} <= cols
    assert any("done" in ix["column_names"] for ix in insp.get_indexes("tasks"))


def test_api_on_migrated_db(migrated):
    from app.db.session import get_db
    from app.main import app

    _, engine = migrated
    Session = sessionmaker(bind=engine, expire_on_commit=False)

    def override():
        with Session() as s:
            yield s

    app.dependency_overrides[get_db] = override
    try:
        client = TestClient(app)
        r = client.post("/api/v1/tasks", json={"title": "Ship it", "due_date": "2026-12-01T10:00:00Z"})
        assert r.status_code == 201, r.text
        task = r.json()
        assert task["due_date"] and task["due_date"].startswith("2026-12-01")
        r = client.patch(f"/api/v1/tasks/{task['id']}", json={"due_date": None})
        assert r.json()["due_date"] is None
    finally:
        app.dependency_overrides.clear()


def test_downgrade_base(migrated):
    from alembic import command

    cfg, engine = migrated
    command.downgrade(cfg, "base")
    assert "tasks" not in sa.inspect(engine).get_table_names()


def test_no_create_all_in_app():
    for path in (ROOT / "app").rglob("*.py"):
        assert "create_all" not in path.read_text(), f"remove create_all from {path.relative_to(ROOT)}; use Alembic"

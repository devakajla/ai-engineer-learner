"""Step 9 checks. Runs with the current directory = the learner's project folder."""

import sqlite3
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path.cwd()


@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")


def make_repo(path):
    from app.repositories.sqlite_task_repository import SqliteTaskRepository

    return SqliteTaskRepository(path)


def task(title="t", priority="medium", done=False, description=None):
    return {"title": title, "description": description, "priority": priority, "done": done}


def test_crud(db_path):
    repo = make_repo(db_path)
    created = repo.add(task("Write SQL", "high"))
    assert created["id"] and created["title"] == "Write SQL" and created["done"] is False
    assert repo.get(created["id"]) == created
    updated = repo.update(created["id"], {"done": True})
    assert updated["done"] is True and updated["title"] == "Write SQL"
    assert repo.delete(created["id"]) is True and repo.get(created["id"]) is None
    assert repo.delete(created["id"]) is False
    assert repo.update(999, {"done": True}) is None


def test_filters_in_sql(db_path):
    repo = make_repo(db_path)
    repo.add(task("a", "high", False))
    repo.add(task("b", "low", True))
    repo.add(task("c", "high", True))
    assert [t["title"] for t in repo.list(done=True)] == ["b", "c"]
    assert [t["title"] for t in repo.list(priority="high")] == ["a", "c"]
    assert [t["title"] for t in repo.list(done=True, priority="high")] == ["c"]
    assert len(repo.list(limit=2)) == 2


def test_persists_across_instances(db_path):
    make_repo(db_path).add(task("kept"))
    assert [t["title"] for t in make_repo(db_path).list()] == ["kept"]


def test_sql_injection_is_harmless(db_path):
    repo = make_repo(db_path)
    evil = "x'); DROP TABLE tasks; --"
    created = repo.add(task(evil))
    assert repo.get(created["id"])["title"] == evil
    assert repo.list(), "table must still exist"


def test_schema_index_and_constraint(db_path):
    make_repo(db_path)
    conn = sqlite3.connect(db_path)
    indexes = [r[1] for r in conn.execute("PRAGMA index_list('tasks')")]
    assert "ix_tasks_done" in indexes, "create an index on tasks(done)"
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tasks (title, priority) VALUES ('x', 'urgent')")
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute("INSERT INTO tasks (title) VALUES (NULL)")


def test_api_uses_sqlite(db_path):
    from app.api.deps import get_task_repository
    from app.main import app

    app.dependency_overrides[get_task_repository] = lambda: make_repo(db_path)
    try:
        client = TestClient(app)
        assert client.get("/api/v1/tasks").json() == []
        created = client.post("/api/v1/tasks", json={"title": "Stored", "priority": "high"}).json()
        assert client.get(f"/api/v1/tasks?done=false&priority=high").json()[0]["id"] == created["id"]
        assert client.patch(f"/api/v1/tasks/{created['id']}", json={"done": True}).json()["done"] is True
        assert client.delete(f"/api/v1/tasks/{created['id']}").status_code == 204
        assert client.get(f"/api/v1/tasks/{created['id']}").status_code == 404
    finally:
        app.dependency_overrides.clear()
    assert make_repo(db_path).list() == []


def test_settings_and_gitignore():
    from app.core.config import Settings

    assert Settings().database_path.endswith(".db")
    assert "*.db" in (ROOT / ".gitignore").read_text(), "ignore database files"


def test_no_values_in_fstring_sql():
    src = (ROOT / "app/repositories/sqlite_task_repository.py").read_text()
    for bad in ("{data[", "{task_id}", "{title}", "{priority}", "{done}"):
        assert bad not in src, "pass values with ? placeholders, never inside f-strings"

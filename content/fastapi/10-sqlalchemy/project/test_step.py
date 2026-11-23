"""Step 10 checks. Runs with the current directory = the learner's project folder."""

import inspect

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.orm import sessionmaker


@pytest.fixture
def session_factory(tmp_path):
    import app.db.models  # noqa: F401  (registers the models on Base.metadata)
    from app.db.base import Base

    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine, sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def client(session_factory):
    from app.db.session import get_db
    from app.main import app

    _, Session = session_factory

    def override():
        with Session() as s:
            yield s

    app.dependency_overrides[get_db] = override
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_model_and_table(session_factory):
    from app.db.models import Task

    engine, _ = session_factory
    assert Task.__tablename__ == "tasks"
    cols = {c["name"] for c in sa_inspect(engine).get_columns("tasks")}
    assert {"id", "title", "description", "priority", "done", "created_at"} <= cols
    assert any("done" in ix["column_names"] for ix in sa_inspect(engine).get_indexes("tasks")), "index tasks.done"


def test_get_db_yields():
    from app.db.session import get_db

    assert inspect.isgeneratorfunction(get_db), "get_db must be a yield dependency"


def test_settings_url():
    from app.core.config import Settings

    assert Settings().database_url.startswith("sqlite")


def test_api_crud(client):
    assert client.get("/api/v1/tasks").json() == []
    r = client.post("/api/v1/tasks", json={"title": "ORM task", "priority": "high"})
    assert r.status_code == 201
    task = r.json()
    assert task["created_at"], "TaskRead should include created_at"
    assert client.get(f"/api/v1/tasks/{task['id']}").json()["title"] == "ORM task"
    assert client.patch(f"/api/v1/tasks/{task['id']}", json={"done": True}).json()["done"] is True
    assert [t["id"] for t in client.get("/api/v1/tasks?done=true&priority=high").json()] == [task["id"]]
    assert client.get("/api/v1/tasks?done=false").json() == []
    assert client.delete(f"/api/v1/tasks/{task['id']}").status_code == 204
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404


def test_repository_with_session(session_factory):
    from app.repositories.task_repository import SqlAlchemyTaskRepository

    _, Session = session_factory
    with Session() as s:
        repo = SqlAlchemyTaskRepository(s)
        t = repo.add({"title": "direct", "description": None, "priority": "low", "done": False})
        assert repo.get(t.id).title == "direct"
        assert repo.update(t.id, {"done": True}).done is True
        assert repo.delete(t.id) is True and repo.get(t.id) is None


def test_read_schema_from_attributes():
    from app.schemas.task import TaskRead

    assert TaskRead.model_config.get("from_attributes") is True

"""Step 6 checks. Runs with the current directory = the learner's project folder."""

import inspect
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path.cwd()

REQUIRED = [
    "app/main.py",
    "app/core/__init__.py",
    "app/core/config.py",
    "app/api/__init__.py",
    "app/api/routes/__init__.py",
    "app/api/routes/health.py",
    "app/api/routes/tasks.py",
    "app/schemas/task.py",
    "app/services/__init__.py",
    "app/services/task_service.py",
    "app/repositories/__init__.py",
    "app/repositories/task_repository.py",
    ".env.example",
]


@pytest.mark.parametrize("path", REQUIRED)
def test_structure(path):
    assert (ROOT / path).exists(), f"missing {path}"


def test_env_not_committed_pattern():
    assert ".env" in (ROOT / ".gitignore").read_text().replace(".venv", ""), ".env must be git-ignored"


def test_settings():
    from app.core.config import Settings, settings

    assert settings.app_name == "TaskFlow"
    assert settings.api_prefix == "/api/v1"
    assert Settings(debug="true").debug is True


def test_settings_read_env(monkeypatch):
    from app.core.config import Settings

    monkeypatch.setenv("APP_NAME", "FromEnv")
    assert Settings().app_name == "FromEnv", "Settings must read environment variables"


def test_versioned_api():
    from app.main import app

    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/api/v1/tasks").status_code == 200
    assert client.get("/tasks").status_code == 404, "task routes must live under /api/v1"

    task = client.post("/api/v1/tasks", json={"title": "Structured"}).json()
    assert client.patch(f"/api/v1/tasks/{task['id']}", json={"done": True}).json()["done"] is True
    assert client.delete(f"/api/v1/tasks/{task['id']}").status_code == 204
    r = client.get(f"/api/v1/tasks/{task['id']}")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}


def test_service_is_http_free():
    from app.repositories.task_repository import InMemoryTaskRepository
    from app.services import task_service as mod

    src = inspect.getsource(mod)
    assert "HTTPException" not in src and "fastapi" not in src, "services must not depend on FastAPI/HTTP"
    service = mod.TaskService(InMemoryTaskRepository())
    with pytest.raises(mod.TaskNotFoundError):
        service.get(12345)


def test_repository_storage_only():
    from app.repositories.task_repository import InMemoryTaskRepository

    repo = InMemoryTaskRepository()
    added = repo.add({"title": "x", "description": None, "priority": "low", "done": False})
    assert repo.get(added["id"]) == added
    assert repo.delete(added["id"]) is True and repo.get(added["id"]) is None


def test_main_is_thin():
    src = (ROOT / "app/main.py").read_text()
    assert "include_router" in src, "main.py should include the routers"
    assert "@app.get" not in src and "@app.post" not in src, "routes belong in app/api/routes/, not main.py"
    assert len([ln for ln in src.splitlines() if ln.strip()]) <= 40, "keep main.py small: wiring only"

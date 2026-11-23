"""Step 8 checks. Runs with the current directory = the learner's project folder."""

from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path.cwd()


def test_deps_module():
    from app.api import deps

    for name in ("get_settings", "get_task_repository", "get_task_service", "TaskServiceDep"):
        assert hasattr(deps, name) or name == "get_settings", f"app/api/deps.py should define {name}"


def test_settings_cached():
    from app.core.config import get_settings

    assert get_settings() is get_settings(), "decorate get_settings with @lru_cache"
    assert get_settings().app_name == "TaskFlow"


def test_create_app_factory():
    from app.main import create_app

    fresh = create_app()
    assert TestClient(fresh).get("/health").json()["status"] == "ok"


def test_routes_use_injected_service():
    from app.api.deps import get_task_service
    from app.main import app
    from app.repositories.task_repository import InMemoryTaskRepository
    from app.services.task_service import TaskService

    client = TestClient(app)
    assert client.get("/api/v1/tasks").json(), "the default repository should contain the seed tasks"

    empty = TaskService(InMemoryTaskRepository())
    app.dependency_overrides[get_task_service] = lambda: empty
    try:
        assert client.get("/api/v1/tasks").json() == [], "routes must get the service via Depends(get_task_service)"
        created = client.post("/api/v1/tasks", json={"title": "Injected"}).json()
        assert empty.get(created["id"])["title"] == "Injected"
        assert client.get(f"/api/v1/tasks/{created['id']}").status_code == 200
        assert client.delete(f"/api/v1/tasks/{created['id']}").status_code == 204
        assert client.get(f"/api/v1/tasks/{created['id']}").status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_no_module_level_service():
    src = (ROOT / "app/api/routes/tasks.py").read_text()
    assert "TaskService(" not in src, "don't construct TaskService in tasks.py — inject it"
    assert "InMemoryTaskRepository(" not in src

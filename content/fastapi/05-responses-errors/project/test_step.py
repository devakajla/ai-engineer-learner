"""Step 5 checks. Runs with the current directory = the learner's project folder."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TASK_FIELDS = {"id", "title", "description", "priority", "done"}


def test_schemas_exist():
    from app.schemas.task import TaskCreate, TaskRead, TaskUpdate  # noqa: F401

    assert set(TaskRead.model_fields) == TASK_FIELDS


def test_create_returns_201():
    r = client.post("/tasks", json={"title": "Lifecycle"})
    assert r.status_code == 201, "POST must return 201 Created"
    assert set(r.json()) == TASK_FIELDS


def test_full_lifecycle():
    task = client.post("/tasks", json={"title": "Lifecycle", "description": "keep me", "priority": "low"}).json()
    tid = task["id"]

    r = client.patch(f"/tasks/{tid}", json={"done": True})
    assert r.status_code == 200
    updated = r.json()
    assert updated["done"] is True
    assert updated["title"] == "Lifecycle" and updated["description"] == "keep me", "PATCH must only change sent fields"

    r = client.patch(f"/tasks/{tid}", json={"description": None, "priority": "high"})
    assert r.json()["description"] is None and r.json()["priority"] == "high"

    r = client.delete(f"/tasks/{tid}")
    assert r.status_code == 204 and r.content == b""

    assert client.get(f"/tasks/{tid}").status_code == 404
    assert client.patch(f"/tasks/{tid}", json={"done": False}).status_code == 404
    assert client.delete(f"/tasks/{tid}").status_code == 404


def test_404_shape():
    r = client.get("/tasks/99999")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}


def test_patch_validation():
    tid = client.post("/tasks", json={"title": "x"}).json()["id"]
    assert client.patch(f"/tasks/{tid}", json={"title": ""}).status_code == 422
    assert client.patch(f"/tasks/{tid}", json={"priority": "urgent"}).status_code == 422
    assert client.patch(f"/tasks/{tid}", json={"id": 5}).status_code == 422


def test_list_shape():
    tasks = client.get("/tasks").json()
    assert tasks and all(set(t) == TASK_FIELDS for t in tasks)


def test_response_models_documented():
    paths = client.get("/openapi.json").json()["paths"]
    ok = paths["/tasks/{task_id}"]["get"]["responses"]["200"]["content"]["application/json"]["schema"]
    assert ok.get("$ref", "").endswith("TaskRead"), "use response_model=TaskRead"

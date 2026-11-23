"""Step 4 checks. Runs with the current directory = the learner's project folder."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_schema_module():
    from app.schemas.task import Priority, TaskCreate

    assert {p.value for p in Priority} == {"low", "medium", "high"}
    fields = set(TaskCreate.model_fields)
    assert {"title", "description", "priority"} <= fields
    assert not {"id", "done"} & fields, "id and done are server-controlled; don't accept them from clients"


def test_create_and_read_back():
    r = client.post("/tasks", json={"title": "  Learn Pydantic  ", "priority": "high"})
    assert r.status_code in (200, 201)
    task = r.json()
    assert task["title"] == "Learn Pydantic", "strip whitespace (str_strip_whitespace=True)"
    assert task["priority"] == "high"
    assert task["done"] is False
    assert isinstance(task["id"], int)
    again = client.get(f"/tasks/{task['id']}")
    assert again.status_code == 200 and again.json()["title"] == "Learn Pydantic"


def test_defaults():
    task = client.post("/tasks", json={"title": "Defaults"}).json()
    assert task["priority"] == "medium"
    assert task.get("description") is None


def test_ids_are_unique():
    a = client.post("/tasks", json={"title": "A"}).json()["id"]
    b = client.post("/tasks", json={"title": "B"}).json()["id"]
    assert a != b


def test_validation():
    assert client.post("/tasks", json={}).status_code == 422
    assert client.post("/tasks", json={"title": ""}).status_code == 422
    assert client.post("/tasks", json={"title": "   "}).status_code == 422
    assert client.post("/tasks", json={"title": "x" * 201}).status_code == 422
    assert client.post("/tasks", json={"title": "ok", "priority": "urgent"}).status_code == 422
    assert client.post("/tasks", json={"title": "ok", "done": True}).status_code == 422, "use extra='forbid'"

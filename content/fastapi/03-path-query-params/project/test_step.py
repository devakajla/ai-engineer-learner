"""Step 3 checks. Runs with the current directory = the learner's project folder."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_still_works():
    assert client.get("/health").json() == {"status": "ok"}


def test_list_tasks():
    r = client.get("/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert isinstance(tasks, list) and len(tasks) >= 3, "seed at least the 3 tasks from the step"
    for t in tasks:
        assert {"id", "title", "priority", "done"} <= t.keys()


def test_filter_done():
    done = client.get("/tasks?done=true").json()
    not_done = client.get("/tasks?done=false").json()
    assert done and all(t["done"] is True for t in done)
    assert not_done and all(t["done"] is False for t in not_done)


def test_filter_priority():
    high = client.get("/tasks?priority=high").json()
    assert high and all(t["priority"] == "high" for t in high)
    assert client.get("/tasks?priority=urgent").status_code == 422, "priority must be an Enum"


def test_limit_bounds():
    assert len(client.get("/tasks?limit=1").json()) == 1
    assert client.get("/tasks?limit=0").status_code == 422
    assert client.get("/tasks?limit=101").status_code == 422


def test_get_one():
    first = client.get("/tasks").json()[0]
    r = client.get(f"/tasks/{first['id']}")
    assert r.status_code == 200 and r.json()["id"] == first["id"]


def test_get_missing_and_invalid():
    assert client.get("/tasks/99999").status_code == 404
    assert client.get("/tasks/abc").status_code == 422
    assert client.get("/tasks/0").status_code == 422, "task_id must be >= 1"

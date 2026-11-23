import pytest


def test_create_returns_201_and_fields(client):
    r = client.post("/api/v1/tasks", json={"title": "  Write tests  ", "priority": "high"})
    assert r.status_code == 201
    task = r.json()
    assert task["title"] == "Write tests"
    assert task["priority"] == "high"
    assert task["done"] is False
    assert task["description"] is None and task["due_date"] is None
    assert task["id"] > 0 and task["created_at"]


def test_create_defaults(make_task):
    assert make_task()["priority"] == "medium"


@pytest.mark.parametrize(
    "payload",
    [{}, {"title": ""}, {"title": "   "}, {"title": "x" * 201}, {"title": "x", "priority": "urgent"}, {"title": "x", "done": True}],
)
def test_create_validation(client, payload):
    assert client.post("/api/v1/tasks", json=payload).status_code == 422


def test_get_one_and_404(client, make_task):
    task = make_task(title="Find me")
    assert client.get(f"/api/v1/tasks/{task['id']}").json()["title"] == "Find me"
    r = client.get("/api/v1/tasks/999")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found", "code": "not_found"}


def test_patch_changes_only_sent_fields(client, make_task):
    task = make_task(title="Keep", description="also keep", priority="low")
    r = client.patch(f"/api/v1/tasks/{task['id']}", json={"done": True, "priority": "high"})
    assert r.status_code == 200
    updated = r.json()
    assert updated["done"] is True and updated["priority"] == "high"
    assert updated["title"] == "Keep" and updated["description"] == "also keep"
    assert client.get(f"/api/v1/tasks/{task['id']}").json()["done"] is True


def test_patch_missing_is_404(client):
    assert client.patch("/api/v1/tasks/999", json={"done": True}).status_code == 404


def test_delete_then_gone(client, make_task):
    task = make_task()
    r = client.delete(f"/api/v1/tasks/{task['id']}")
    assert r.status_code == 204 and r.content == b""
    assert client.get(f"/api/v1/tasks/{task['id']}").status_code == 404
    assert client.delete(f"/api/v1/tasks/{task['id']}").status_code == 404


def test_list_envelope_and_paging(client, make_task):
    for i in range(5):
        make_task(title=f"T{i}")
    body = client.get("/api/v1/tasks?limit=2&offset=1&sort=id").json()
    assert body["total"] == 5 and body["limit"] == 2 and body["offset"] == 1
    assert [t["title"] for t in body["items"]] == ["T1", "T2"]


def test_list_filters(client, make_task):
    a = make_task(title="open high", priority="high")
    b = make_task(title="done high", priority="high")
    make_task(title="open low", priority="low")
    client.patch(f"/api/v1/tasks/{b['id']}", json={"done": True})
    done = client.get("/api/v1/tasks?done=true").json()
    assert [t["id"] for t in done["items"]] == [b["id"]] and done["total"] == 1
    open_high = client.get("/api/v1/tasks?done=false&priority=high").json()
    assert [t["id"] for t in open_high["items"]] == [a["id"]]


def test_search_and_sort(client, make_task):
    make_task(title="Banana report")
    make_task(title="apple report")
    make_task(title="Cherry")
    body = client.get("/api/v1/tasks?q=REPORT&sort=title").json()
    assert [t["title"] for t in body["items"]] == ["Banana report", "apple report"]
    assert client.get("/api/v1/tasks?sort=bogus").status_code == 422


def test_due_date_roundtrip(client, make_task):
    task = make_task(due_date="2026-12-31T18:00:00Z")
    assert task["due_date"].startswith("2026-12-31")
    cleared = client.patch(f"/api/v1/tasks/{task['id']}", json={"due_date": None}).json()
    assert cleared["due_date"] is None

import pytest
from fastapi.testclient import TestClient

from app_under_test import NoteRepo, app, get_repo


@pytest.fixture
def client():
    repo = NoteRepo()
    app.dependency_overrides[get_repo] = lambda: repo
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create(client):
    r = client.post("/notes", json={"text": "hello"})
    assert r.status_code == 201
    assert r.json() == {"id": 1, "text": "hello", "pinned": False}
    assert client.post("/notes", json={"text": ""}).status_code == 422


def test_pinned_first(client):
    client.post("/notes", json={"text": "a"})
    client.post("/notes", json={"text": "b", "pinned": True})
    client.post("/notes", json={"text": "c"})
    assert [n["text"] for n in client.get("/notes").json()] == ["b", "a", "c"]


def test_patch_partial(client):
    client.post("/notes", json={"text": "keep", "pinned": True})
    r = client.patch("/notes/1", json={"pinned": False})
    assert r.json() == {"id": 1, "text": "keep", "pinned": False}
    assert client.patch("/notes/99", json={"pinned": True}).status_code == 404


def test_delete(client):
    client.post("/notes", json={"text": "bye"})
    assert client.delete("/notes/1").status_code == 204
    assert client.get("/notes").json() == []
    assert client.patch("/notes/1", json={"pinned": True}).status_code == 404

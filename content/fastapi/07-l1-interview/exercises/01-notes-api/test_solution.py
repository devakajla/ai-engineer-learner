from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def setup_function():
    solution.NOTES.clear()


def make(title="t", body=""):
    return client.post("/notes", json={"title": title, "body": body})


def test_create():
    r = make("First", "hello")
    assert r.status_code == 201, "creating should return 201"
    assert r.json() == {"id": 1, "title": "First", "body": "hello"}
    assert make("Second").json() == {"id": 2, "title": "Second", "body": ""}


def test_create_validation():
    assert client.post("/notes", json={"title": ""}).status_code == 422
    assert client.post("/notes", json={"title": "x" * 101}).status_code == 422
    assert client.post("/notes", json={}).status_code == 422


def test_get_and_404():
    make("A")
    assert client.get("/notes/1").json()["title"] == "A"
    r = client.get("/notes/99")
    assert r.status_code == 404 and r.json() == {"detail": "Note not found"}


def test_list_pagination():
    for i in range(12):
        make(f"n{i}")
    page = client.get("/notes").json()
    assert [n["id"] for n in page] == list(range(1, 11)), "default limit is 10, ordered by id"
    assert [n["id"] for n in client.get("/notes?limit=5&offset=10").json()] == [11, 12]
    assert client.get("/notes?limit=0").status_code == 422
    assert client.get("/notes?limit=51").status_code == 422
    assert client.get("/notes?offset=-1").status_code == 422


def test_patch_only_sent_fields():
    make("Title", "Body")
    r = client.patch("/notes/1", json={"body": "New body"})
    assert r.json() == {"id": 1, "title": "Title", "body": "New body"}
    assert client.patch("/notes/1", json={"title": "New"}).json()["body"] == "New body"
    assert client.patch("/notes/1", json={"title": ""}).status_code == 422
    assert client.patch("/notes/7", json={"title": "x"}).status_code == 404


def test_delete():
    make("A")
    r = client.delete("/notes/1")
    assert r.status_code == 204 and r.content == b"", "204 must have an empty body"
    assert client.get("/notes/1").status_code == 404
    assert client.delete("/notes/1").status_code == 404

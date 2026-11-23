from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_create_201():
    r = client.post("/bookmarks", json={"url": "https://fastapi.tiangolo.com", "title": "FastAPI"})
    assert r.status_code == 201
    body = r.json()
    assert body["url"] == "https://fastapi.tiangolo.com" and isinstance(body["id"], int)


def test_duplicate_409():
    client.post("/bookmarks", json={"url": "https://dup.io", "title": "a"})
    r = client.post("/bookmarks", json={"url": "https://dup.io", "title": "b"})
    assert r.status_code == 409
    assert r.json() == {"detail": "Bookmark already exists"}


def test_delete_204_then_404():
    bid = client.post("/bookmarks", json={"url": "https://del.io", "title": "x"}).json()["id"]
    r = client.delete(f"/bookmarks/{bid}")
    assert r.status_code == 204
    assert r.content == b"", "204 must have an empty body"
    r2 = client.delete(f"/bookmarks/{bid}")
    assert r2.status_code == 404 and r2.json() == {"detail": "Bookmark not found"}

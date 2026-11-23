from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_get():
    r = client.get("/items")
    assert r.status_code == 200 and r.json() == []


def test_post():
    assert client.post("/items").json() == {"created": True}


def test_delete():
    assert client.delete("/items").json() == {"deleted": 0}


def test_other_method_is_405():
    assert client.put("/items").status_code == 405
    assert client.get("/nope").status_code == 404

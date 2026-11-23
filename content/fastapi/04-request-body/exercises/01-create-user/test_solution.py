from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_valid_user():
    r = client.post("/users", json={"name": " Dev ", "email": "dev@x.io", "age": 22})
    assert r.status_code == 200
    assert r.json() == {"id": 1, "name": "Dev", "email": "dev@x.io", "age": 22, "bio": None}


def test_invalid_fields():
    base = {"name": "Dev", "email": "dev@x.io", "age": 22}
    assert client.post("/users", json={**base, "name": "   "}).status_code == 422
    assert client.post("/users", json={**base, "email": "nope"}).status_code == 422
    assert client.post("/users", json={**base, "age": 12}).status_code == 422
    assert client.post("/users", json={**base, "bio": "x" * 201}).status_code == 422


def test_missing_and_extra():
    assert client.post("/users", json={"name": "Dev", "age": 22}).status_code == 422
    r = client.post("/users", json={"name": "Dev", "email": "d@x.io", "age": 22, "is_admin": True})
    assert r.status_code == 422, "unknown fields must be rejected (extra='forbid')"

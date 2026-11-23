from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_by_id():
    assert client.get("/users/7").json() == {"user_id": 7}


def test_me_route_order():
    r = client.get("/users/me")
    assert r.status_code == 200, "put /users/me ABOVE /users/{user_id}"
    assert r.json() == {"user_id": "me"}


def test_validation():
    assert client.get("/users/0").status_code == 422, "user_id must be >= 1"
    assert client.get("/users/abc").status_code == 422

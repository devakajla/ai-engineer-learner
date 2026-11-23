from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json() == {"message": "Hello, TaskFlow"}
    assert r.headers["content-type"].startswith("application/json")

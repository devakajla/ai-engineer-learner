from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_all_sources():
    r = client.put("/notes/5?notify=true", json={"text": "Buy milk"})
    assert r.status_code == 200
    assert r.json() == {"note_id": 5, "notify": True, "note": {"text": "Buy milk", "pinned": False}}


def test_defaults():
    r = client.put("/notes/1", json={"text": "a", "pinned": True})
    assert r.json() == {"note_id": 1, "notify": False, "note": {"text": "a", "pinned": True}}


def test_validation():
    assert client.put("/notes/0", json={"text": "a"}).status_code == 422
    assert client.put("/notes/1", json={"text": ""}).status_code == 422
    assert client.put("/notes/1").status_code == 422, "body is required"

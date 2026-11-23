from fastapi.testclient import TestClient

from app_under_test import app

client = TestClient(app)


def test_quote_works():
    r = client.post("/quote", json={"items": [{"price": 10, "qty": 1}]})
    assert r.status_code == 200

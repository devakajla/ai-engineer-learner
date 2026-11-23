from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def setup_function():
    solution.PAYMENTS.clear()
    solution.IDEMPOTENCY_STORE.clear()


def test_no_key_creates_each_time():
    client.post("/payments", json={"amount": 100, "currency": "INR"})
    client.post("/payments", json={"amount": 100, "currency": "INR"})
    assert len(solution.PAYMENTS) == 2


def test_replay_same_key_same_body():
    h = {"Idempotency-Key": "k1"}
    first = client.post("/payments", json={"amount": 500, "currency": "INR"}, headers=h)
    second = client.post("/payments", json={"amount": 500, "currency": "INR"}, headers=h)
    assert first.status_code == second.status_code == 201
    assert first.json() == second.json()
    assert second.headers.get("Idempotent-Replayed") == "true"
    assert "Idempotent-Replayed" not in first.headers
    assert len(solution.PAYMENTS) == 1, "a retry must not create a second payment"


def test_same_key_different_body():
    h = {"Idempotency-Key": "k2"}
    client.post("/payments", json={"amount": 1, "currency": "INR"}, headers=h)
    r = client.post("/payments", json={"amount": 2, "currency": "INR"}, headers=h)
    assert r.status_code == 422
    assert r.json() == {"detail": "Idempotency-Key reused with a different request"}
    assert len(solution.PAYMENTS) == 1


def test_different_keys():
    client.post("/payments", json={"amount": 1, "currency": "INR"}, headers={"Idempotency-Key": "a"})
    client.post("/payments", json={"amount": 1, "currency": "INR"}, headers={"Idempotency-Key": "b"})
    assert len(solution.PAYMENTS) == 2

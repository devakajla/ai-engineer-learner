from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)
VALID = {"email": "Dev@Example.com", "password": "secret123", "name": "Dev"}


def setup_function():
    solution.USERS.clear()


def test_create_user_hides_password():
    r = client.post("/users", json=VALID)
    assert r.status_code == 201
    assert r.json() == {"id": 1, "email": "dev@example.com", "name": "Dev"}, "email is lower-cased, no password"
    assert "password" not in r.text


def test_get_user_hides_password():
    client.post("/users", json=VALID)
    r = client.get("/users/1")
    assert r.json() == {"id": 1, "email": "dev@example.com", "name": "Dev"}
    assert "password" not in r.text
    missing = client.get("/users/9")
    assert missing.status_code == 404 and missing.json() == {"detail": "User not found"}


def test_duplicate_email_is_409():
    client.post("/users", json=VALID)
    r = client.post("/users", json={**VALID, "email": "DEV@example.COM", "name": "Other"})
    assert r.status_code == 409 and r.json() == {"detail": "Email already registered"}
    assert len(solution.USERS) == 1


def test_ids_increase():
    client.post("/users", json=VALID)
    r = client.post("/users", json={**VALID, "email": "two@example.com"})
    assert r.json()["id"] == 2


def test_validation():
    for bad in (
        {**VALID, "email": "not-an-email"},
        {**VALID, "email": "a@b"},
        {**VALID, "password": "short"},
        {**VALID, "name": ""},
        {**VALID, "name": "x" * 51},
    ):
        assert client.post("/users", json=bad).status_code == 422, f"should reject {bad}"
    assert client.post("/users", json={"email": "a@b.co"}).status_code == 422, "missing fields"


def test_unknown_fields_rejected():
    r = client.post("/users", json={**VALID, "is_admin": True})
    assert r.status_code == 422, "extra fields must be rejected (mass assignment)"
    assert solution.USERS == []

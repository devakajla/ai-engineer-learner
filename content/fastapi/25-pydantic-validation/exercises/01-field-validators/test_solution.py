import pytest
from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_cleans_username():
    r = client.post("/signup", json={"username": "  Dev_99 ", "password": "secret123"})
    assert r.status_code == 201, r.text
    assert r.json() == {"username": "dev_99"}, "send back only the cleaned username"


@pytest.mark.parametrize(
    "username",
    ["a!", "ab", "x" * 21, "has space", "dot.dot", "   ", "ab "],
)
def test_bad_usernames(username):
    r = client.post("/signup", json={"username": username, "password": "secret123"})
    assert r.status_code == 422, f"{username!r} should be rejected"


def test_length_is_checked_after_cleaning():
    assert client.post("/signup", json={"username": "  abc  ", "password": "secret123"}).status_code == 201
    assert client.post("/signup", json={"username": "  ab  ", "password": "secret123"}).status_code == 422


@pytest.mark.parametrize("password", ["short1", "onlyletters", "12345678", ""])
def test_bad_passwords(password):
    r = client.post("/signup", json={"username": "devdev", "password": password})
    assert r.status_code == 422, f"{password!r} should be rejected"


def test_error_points_at_field():
    r = client.post("/signup", json={"username": "devdev", "password": "short1"})
    assert r.json()["detail"][0]["loc"] == ["body", "password"]


def test_password_never_returned():
    r = client.post("/signup", json={"username": "devdev", "password": "secret123"})
    assert "password" not in r.text

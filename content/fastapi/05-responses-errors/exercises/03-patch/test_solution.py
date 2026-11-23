from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def setup_function():
    solution.PROFILE.clear()
    solution.PROFILE.update({"name": "Dev", "bio": "Backend dev", "city": "Pune"})


def test_partial_update():
    r = client.patch("/profile", json={"city": "Bengaluru"})
    assert r.json() == {"name": "Dev", "bio": "Backend dev", "city": "Bengaluru"}


def test_explicit_null_clears():
    assert client.patch("/profile", json={"bio": None}).json() == {"name": "Dev", "bio": None, "city": "Pune"}


def test_empty_patch_changes_nothing():
    assert client.patch("/profile", json={}).json() == {"name": "Dev", "bio": "Backend dev", "city": "Pune"}


def test_validation():
    assert client.patch("/profile", json={"name": ""}).status_code == 422

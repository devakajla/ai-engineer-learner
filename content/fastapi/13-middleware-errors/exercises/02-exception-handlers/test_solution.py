import inspect

from fastapi.testclient import TestClient

import solution
from solution import AppError, app

client = TestClient(app, raise_server_exceptions=False)


def test_not_found():
    r = client.get("/users/99")
    assert r.status_code == 404 and r.json() == {"detail": "User 99 not found", "code": "not_found"}


def test_conflict():
    r = client.post("/users?email=dev@x.io")
    assert r.status_code == 409 and r.json() == {"detail": "Email already registered", "code": "conflict"}
    assert client.post("/users?email=new@x.io").status_code == 201


def test_generic_app_error():
    @app.get("/generic")
    async def generic():
        raise AppError("bad thing")

    r = client.get("/generic")
    assert r.status_code == 400 and r.json() == {"detail": "bad thing", "code": "app_error"}


def test_500_hides_details():
    r = client.get("/boom")
    assert r.status_code == 500
    assert r.json() == {"detail": "Internal server error", "code": "internal_error"}
    assert "secret" not in r.text


def test_mapping_not_in_error_classes():
    assert hasattr(solution, "STATUS_FOR")
    assert "status" not in inspect.getsource(solution.NotFoundError).lower()

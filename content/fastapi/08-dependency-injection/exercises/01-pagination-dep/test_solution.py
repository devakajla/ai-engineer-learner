import inspect

from fastapi.testclient import TestClient

import solution
from solution import app

client = TestClient(app)


def test_defaults():
    assert len(client.get("/items").json()) == 20
    assert client.get("/users").json()[0] == "user-0"


def test_paging():
    assert client.get("/items?limit=5&offset=10").json() == [f"item-{i}" for i in range(10, 15)]
    assert client.get("/users?limit=100&offset=25").json() == [f"user-{i}" for i in range(25, 30)]


def test_validation_shared():
    for path in ("/items", "/users"):
        for q in ("limit=0", "limit=101", "offset=-1"):
            assert client.get(f"{path}?{q}").status_code == 422


def test_uses_dependency():
    src = inspect.getsource(solution)
    assert "Depends(pagination)" in src, "define PaginationDep with Depends(pagination)"
    assert src.count("Query(ge=1, le=100)") == 1, "the limit rule should live only in the dependency"

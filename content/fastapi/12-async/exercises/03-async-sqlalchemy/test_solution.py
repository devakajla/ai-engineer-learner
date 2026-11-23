import inspect

from fastapi.testclient import TestClient

import solution
from solution import app


def test_flow():
    with TestClient(app) as client:
        r = client.post("/items", json={"name": "pen", "qty": 5})
        assert r.status_code == 201
        item = r.json()
        assert client.patch(f"/items/{item['id']}/qty?delta=-3").json()["qty"] == 2
        r = client.patch(f"/items/{item['id']}/qty?delta=-3")
        assert r.status_code == 409 and r.json() == {"detail": "Not enough stock"}
        assert client.patch("/items/999/qty?delta=1").status_code == 404
        names = [i["name"] for i in client.get("/items").json()]
        assert "pen" in names
        assert client.post("/items", json={"name": "", "qty": 1}).status_code == 422


def test_everything_async():
    for fn in (solution.create_item, solution.list_items, solution.change_qty, solution.init_db):
        assert inspect.iscoroutinefunction(fn), f"{fn.__name__} must be async"
    assert inspect.isasyncgenfunction(solution.get_db), "get_db must be an async generator"
    assert "aiosqlite" in str(solution.engine.url)

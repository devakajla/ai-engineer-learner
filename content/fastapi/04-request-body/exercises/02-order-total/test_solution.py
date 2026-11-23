from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def order(items):
    return {"customer": "Dev", "items": items}


def test_total():
    r = client.post(
        "/orders",
        json=order([{"name": "pen", "quantity": 2, "unit_price": 25}, {"name": "book", "quantity": 1, "unit_price": 200}]),
    )
    assert r.status_code == 200
    assert r.json() == {"customer": "Dev", "item_count": 2, "total": 250.0}


def test_rounding():
    r = client.post("/orders", json=order([{"name": "x", "quantity": 3, "unit_price": 0.1}]))
    assert r.json()["total"] == 0.3


def test_validation():
    assert client.post("/orders", json=order([])).status_code == 422
    assert client.post("/orders", json=order([{"name": "x", "quantity": 0, "unit_price": 1}])).status_code == 422
    assert client.post("/orders", json=order([{"name": "x", "quantity": 1, "unit_price": -5}])).status_code == 422


def test_nested_error_location():
    r = client.post(
        "/orders",
        json=order([{"name": "ok", "quantity": 1, "unit_price": 1}, {"name": "bad", "quantity": 0, "unit_price": 1}]),
    )
    locs = [e["loc"] for e in r.json()["detail"]]
    assert ["body", "items", 1, "quantity"] in locs

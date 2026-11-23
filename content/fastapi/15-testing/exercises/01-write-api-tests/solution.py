import pytest
from fastapi.testclient import TestClient

from app_under_test import app

client = TestClient(app)


def quote(items, coupon=None):
    return client.post("/quote", json={"items": items, "coupon": coupon})


def test_subtotal_uses_qty():
    assert quote([{"price": 10, "qty": 3}, {"price": 5, "qty": 2}]).json() == {"subtotal": 40, "discount": 0, "total": 40}


def test_coupon_ten_percent():
    assert quote([{"price": 200, "qty": 1}], "SAVE10").json() == {"subtotal": 200, "discount": 20, "total": 180}


def test_unknown_coupon_rejected():
    r = quote([{"price": 10, "qty": 1}], "FREE")
    assert r.status_code == 400 and r.json() == {"detail": "Invalid coupon"}


@pytest.mark.parametrize(("price", "discount"), [(999.99, 0), (1000, 50), (1500, 50)])
def test_bulk_threshold(price, discount):
    body = quote([{"price": price, "qty": 1}]).json()
    assert body["discount"] == discount


def test_rounding():
    body = quote([{"price": 0.1, "qty": 3}]).json()
    assert body == {"subtotal": 0.3, "discount": 0, "total": 0.3}


@pytest.mark.parametrize(
    "items", [[], [{"price": 0, "qty": 1}], [{"price": 5, "qty": 0}], [{"price": -1, "qty": 1}]]
)
def test_validation(items):
    assert quote(items).status_code == 422

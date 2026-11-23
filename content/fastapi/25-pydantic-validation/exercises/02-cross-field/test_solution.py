import pytest
from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def body(**changes):
    data = {"guest": "Ana", "check_in": "2026-03-01", "check_out": "2026-03-04"}
    data.update(changes)
    return data


def test_valid_booking_with_nights():
    r = client.post("/bookings", json=body())
    assert r.status_code == 201, r.text
    assert r.json() == {
        "guest": "Ana",
        "check_in": "2026-03-01",
        "check_out": "2026-03-04",
        "rooms": 1,
        "nights": 3,
    }


def test_nights_across_month_end():
    r = client.post("/bookings", json=body(check_in="2026-02-27", check_out="2026-03-02"))
    assert r.json()["nights"] == 3


@pytest.mark.parametrize("check_out", ["2026-03-01", "2026-02-28"])
def test_checkout_must_be_after_checkin(check_out):
    r = client.post("/bookings", json=body(check_out=check_out))
    assert r.status_code == 422, "same day or earlier must be rejected"


def test_one_night_is_ok():
    r = client.post("/bookings", json=body(check_out="2026-03-02"))
    assert r.status_code == 201 and r.json()["nights"] == 1


@pytest.mark.parametrize("rooms", [0, 6])
def test_rooms_limits(rooms):
    assert client.post("/bookings", json=body(rooms=rooms)).status_code == 422


def test_rooms_value_is_kept():
    assert client.post("/bookings", json=body(rooms=3)).json()["rooms"] == 3


@pytest.mark.parametrize("change", [{"guest": ""}, {"check_in": "not-a-date"}])
def test_other_validation(change):
    assert client.post("/bookings", json=body(**change)).status_code == 422

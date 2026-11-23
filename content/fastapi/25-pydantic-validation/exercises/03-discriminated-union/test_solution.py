import pytest
from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_email():
    r = client.post("/notify", json={"channel": "email", "to": "a@x.io", "subject": "Hi"})
    assert r.status_code == 200, r.text
    assert r.json() == {"sent_via": "email", "target": "a@x.io"}


def test_sms():
    r = client.post("/notify", json={"channel": "sms", "phone": "9876543210"})
    assert r.json() == {"sent_via": "sms", "target": "9876543210"}


def test_push():
    r = client.post("/notify", json={"channel": "push", "device_id": "dev-1"})
    assert r.json() == {"sent_via": "push", "target": "dev-1"}


@pytest.mark.parametrize(
    "body",
    [
        {"channel": "fax", "phone": "9876543210"},
        {"phone": "9876543210"},
        {"channel": "email", "to": "no-at-sign", "subject": "Hi"},
        {"channel": "email", "to": "a@x.io", "subject": ""},
        {"channel": "email", "to": "a@x.io"},
        {"channel": "sms", "phone": "12345"},
        {"channel": "sms", "phone": "98765abcde"},
        {"channel": "push", "device_id": ""},
    ],
)
def test_invalid_bodies(body):
    assert client.post("/notify", json=body).status_code == 422, f"{body} should be rejected"


def test_error_mentions_the_chosen_model_only():
    r = client.post("/notify", json={"channel": "sms", "phone": "12345"})
    locs = [tuple(e["loc"]) for e in r.json()["detail"]]
    assert all("sms" in loc for loc in locs), f"errors should point inside the sms model, got {locs}"
    assert not any("email" in loc or "push" in loc for loc in locs)

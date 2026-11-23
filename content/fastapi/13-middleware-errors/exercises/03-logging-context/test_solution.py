import logging

from fastapi.testclient import TestClient

from solution import RequestIdFilter, app, request_id_var

client = TestClient(app)


def test_logs_have_request_id(caplog):
    caplog.set_level(logging.INFO, logger="notes")
    r = client.get("/notes", headers={"X-Request-ID": "req-123"})
    assert r.json() == [] and r.headers["X-Request-ID"] == "req-123"
    records = [rec for rec in caplog.records if rec.name == "notes"]
    messages = [rec.getMessage() for rec in records]
    assert "listing notes" in messages
    assert "GET /notes -> 200" in messages, "log one access line per request"
    assert all(getattr(rec, "request_id", None) == "req-123" for rec in records)


def test_generated_and_isolated(caplog):
    caplog.set_level(logging.INFO, logger="notes")
    r = client.get("/notes")
    rid = r.headers["X-Request-ID"]
    assert len(rid) == 32
    assert all(rec.request_id == rid for rec in caplog.records if rec.name == "notes")
    assert request_id_var.get() == "-", "reset the ContextVar after the request"


def test_filter_default():
    record = logging.LogRecord("x", logging.INFO, __file__, 1, "m", None, None)
    assert RequestIdFilter().filter(record) is True and record.request_id == "-"

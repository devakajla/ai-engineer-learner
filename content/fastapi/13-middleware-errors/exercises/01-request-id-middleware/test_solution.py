from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_echo_request_id():
    r = client.get("/whoami", headers={"X-Request-ID": "abc"})
    assert r.json() == {"request_id": "abc"}
    assert r.headers["X-Request-ID"] == "abc"


def test_generated_id_and_timing():
    r = client.get("/whoami")
    rid = r.json()["request_id"]
    assert len(rid) == 32 and r.headers["X-Request-ID"] == rid
    assert float(r.headers["X-Process-Time-Ms"]) >= 0


def test_headers_on_404():
    r = client.get("/missing")
    assert r.status_code == 404 and "X-Request-ID" in r.headers


def test_cors():
    ok = client.options(
        "/whoami", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"}
    )
    assert ok.headers.get("access-control-allow-origin") == "http://localhost:3000"
    bad = client.get("/whoami", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in bad.headers

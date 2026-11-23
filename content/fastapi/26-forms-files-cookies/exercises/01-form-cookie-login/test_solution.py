from fastapi.testclient import TestClient

from solution import app


def fresh():
    return TestClient(app)


def test_login_ok_sets_cookie():
    client = fresh()
    r = client.post("/login", data={"username": "dev", "password": "secret123"})
    assert r.status_code == 200, r.text
    assert r.json() == {"ok": True}
    header = r.headers["set-cookie"]
    assert "session=abc123" in header
    assert "httponly" in header.lower(), "the session cookie must be HttpOnly"


def test_login_wrong_password():
    client = fresh()
    r = client.post("/login", data={"username": "dev", "password": "nope"})
    assert r.status_code == 401
    assert r.json() == {"detail": "Wrong username or password"}
    assert "set-cookie" not in r.headers


def test_login_wrong_user():
    r = fresh().post("/login", data={"username": "ann", "password": "secret123"})
    assert r.status_code == 401


def test_login_needs_form_fields():
    assert fresh().post("/login", data={"username": "dev"}).status_code == 422


def test_login_is_form_not_json():
    r = fresh().post("/login", json={"username": "dev", "password": "secret123"})
    assert r.status_code == 422, "the route must read form data, not a JSON body"


def test_me_after_login_uses_cookie():
    client = fresh()
    client.post("/login", data={"username": "dev", "password": "secret123"})
    r = client.get("/me")
    assert r.status_code == 200 and r.json() == {"user": "dev"}


def test_me_without_cookie():
    r = fresh().get("/me")
    assert r.status_code == 401
    assert r.json() == {"detail": "Not logged in"}


def test_me_with_wrong_cookie():
    client = fresh()
    client.cookies.set("session", "wrong")
    assert client.get("/me").status_code == 401

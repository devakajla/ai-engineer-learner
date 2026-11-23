from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)
GZIP = {"Accept-Encoding": "gzip"}


def test_small_is_not_compressed():
    r = client.get("/small", headers=GZIP)
    assert r.status_code == 200 and r.json() == {"ok": True}
    assert "content-encoding" not in r.headers, "answers under 1000 bytes stay plain"


def test_big_is_compressed():
    r = client.get("/big", headers=GZIP)
    assert r.status_code == 200
    assert r.headers.get("content-encoding") == "gzip"
    assert r.json() == {"data": "x" * 2000}, "the client must get the same data after unzipping"


def test_no_gzip_if_client_does_not_accept_it():
    r = client.get("/big", headers={"Accept-Encoding": "identity"})
    assert "content-encoding" not in r.headers


def test_mounted_sub_app():
    r = client.get("/admin/stats")
    assert r.status_code == 200 and r.json() == {"admin": True}
    assert client.get("/stats").status_code == 404, "the sub-app routes live only under /admin"


def test_allowed_hosts():
    assert client.get("/small", headers={"Host": "api.example.com"}).status_code == 200
    assert client.get("/small").status_code == 200


def test_bad_host_rejected():
    r = client.get("/small", headers={"Host": "evil.com"})
    assert r.status_code == 400


def test_bad_host_rejected_for_sub_app_too():
    assert client.get("/admin/stats", headers={"Host": "evil.com"}).status_code == 400

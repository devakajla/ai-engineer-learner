from fastapi.testclient import TestClient

from solution import app, encode_base62

client = TestClient(app, follow_redirects=False)


def test_base62():
    assert [encode_base62(n) for n in (1, 9, 10, 35, 36, 61, 62, 3843, 3844)] == ["1", "9", "a", "z", "A", "Z", "10", "ZZ", "100"]


def test_shorten_redirect_stats():
    r = client.post("/links", json={"url": "https://fastapi.tiangolo.com/tutorial/"})
    assert r.status_code == 201
    code = r.json()["code"]
    for _ in range(3):
        red = client.get(f"/{code}")
        assert red.status_code == 307 and red.headers["location"] == "https://fastapi.tiangolo.com/tutorial/"
    assert client.get(f"/links/{code}/stats").json() == {"code": code, "url": "https://fastapi.tiangolo.com/tutorial/", "hits": 3}


def test_idempotent():
    a = client.post("/links", json={"url": "https://example.com/a"})
    b = client.post("/links", json={"url": "https://example.com/a"})
    assert a.status_code == 201 and b.status_code == 200
    assert a.json()["code"] == b.json()["code"]


def test_errors():
    assert client.post("/links", json={"url": "ftp://x"}).status_code == 422
    assert client.post("/links", json={"url": "not a url"}).status_code == 422
    r = client.get("/nope123")
    assert r.status_code == 404 and r.json() == {"detail": "Link not found"}
    assert client.get("/links/nope/stats").status_code == 404

from fastapi.testclient import TestClient

from solution import Settings, app, get_settings

client = TestClient(app)


def test_requires_key():
    r = client.get("/admin/stats")
    assert r.status_code == 401 and r.json() == {"detail": "Invalid API key"}
    assert client.get("/admin/stats", headers={"X-API-Key": "wrong"}).status_code == 401


def test_valid_key():
    r = client.get("/admin/stats", headers={"X-API-Key": "dev-key"})
    assert r.status_code == 200 and r.json() == {"tasks": 42}


def test_public():
    assert client.get("/public").json() == {"ok": True}


def test_settings_override():
    app.dependency_overrides[get_settings] = lambda: Settings(api_key="test-key")
    try:
        assert client.get("/admin/stats", headers={"X-API-Key": "test-key"}).status_code == 200
        assert client.get("/admin/stats", headers={"X-API-Key": "dev-key"}).status_code == 401
    finally:
        app.dependency_overrides.clear()


def test_cached():
    assert get_settings() is get_settings(), "use @lru_cache on get_settings"

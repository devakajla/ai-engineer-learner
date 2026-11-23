from fastapi.testclient import TestClient

from solution import app

client = TestClient(app)


def test_openapi_metadata():
    info = client.get("/openapi.json").json()["info"]
    assert info["title"] == "TaskFlow"
    assert info["version"] == "0.1.0"
    assert info.get("description") == "Manage your tasks"


def test_about():
    assert client.get("/about").json() == {"name": "TaskFlow", "version": "0.1.0"}


def test_about_reads_from_app():
    app.version = "9.9.9"
    try:
        assert client.get("/about").json()["version"] == "9.9.9", "read app.version, don't hard-code it"
    finally:
        app.version = "0.1.0"

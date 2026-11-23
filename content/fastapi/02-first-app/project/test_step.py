"""Step 2 checks. Runs with the current directory = the learner's project folder."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_app_metadata():
    assert app.title == "TaskFlow", "set FastAPI(title='TaskFlow')"
    assert app.version == "0.1.0", "set FastAPI(version='0.1.0')"


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_docs_available():
    assert client.get("/openapi.json").status_code == 200
    assert "/health" in client.get("/openapi.json").json()["paths"]

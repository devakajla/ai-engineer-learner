import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from solution import app, get_settings

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in ("APP_NAME", "DEBUG", "MAX_PAGE_SIZE"):
        monkeypatch.delenv(name, raising=False)


def test_defaults():
    assert client.get("/config").json() == {"app_name": "Notes", "debug": False, "max_page_size": 50}


def test_env_overrides(monkeypatch):
    monkeypatch.setenv("APP_NAME", "TaskFlow")
    monkeypatch.setenv("DEBUG", "true")
    monkeypatch.setenv("MAX_PAGE_SIZE", "10")
    assert client.get("/config").json() == {"app_name": "TaskFlow", "debug": True, "max_page_size": 10}


def test_invalid_env(monkeypatch):
    monkeypatch.setenv("MAX_PAGE_SIZE", "abc")
    with pytest.raises(ValidationError):
        get_settings()

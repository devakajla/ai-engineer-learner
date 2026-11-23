import json

import pytest

import solution
from solution import load_settings


@pytest.fixture(autouse=True)
def no_env(monkeypatch):
    monkeypatch.delenv("APP_PORT", raising=False)


def test_missing_file_gives_defaults(tmp_path):
    assert load_settings(tmp_path / "missing.json") == {"debug": False, "port": 8000, "name": "app"}


def test_file_overrides_defaults(tmp_path):
    file = tmp_path / "s.json"
    file.write_text(json.dumps({"port": 9000, "debug": True}))
    assert load_settings(file) == {"debug": True, "port": 9000, "name": "app"}


def test_env_overrides_file(tmp_path, monkeypatch):
    file = tmp_path / "s.json"
    file.write_text(json.dumps({"port": 9000, "debug": True}))
    monkeypatch.setenv("APP_PORT", "7000")
    assert load_settings(file) == {"debug": True, "port": 7000, "name": "app"}


def test_env_without_file(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_PORT", "1234")
    assert load_settings(tmp_path / "none.json")["port"] == 1234


def test_bad_json(tmp_path):
    file = tmp_path / "s.json"
    file.write_text("{not json")
    with pytest.raises(ValueError):
        load_settings(file)


def test_json_not_an_object(tmp_path):
    file = tmp_path / "s.json"
    file.write_text("[1, 2]")
    with pytest.raises(ValueError):
        load_settings(file)


def test_bad_port_env(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_PORT", "abc")
    with pytest.raises(ValueError):
        load_settings(tmp_path / "none.json")


def test_defaults_are_not_shared(tmp_path):
    first = load_settings(tmp_path / "none.json")
    first["port"] = 1
    first["extra"] = True
    assert load_settings(tmp_path / "none.json") == {"debug": False, "port": 8000, "name": "app"}
    assert solution.DEFAULTS == {"debug": False, "port": 8000, "name": "app"}

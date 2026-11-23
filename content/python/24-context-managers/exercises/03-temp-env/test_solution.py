import os

import pytest

from solution import temp_env


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.setenv("MODE", "dev")
    monkeypatch.delenv("NEW_VAR", raising=False)


def test_set_and_restore():
    with temp_env(MODE="test", NEW_VAR="1"):
        assert os.environ["MODE"] == "test" and os.environ["NEW_VAR"] == "1"
    assert os.environ["MODE"] == "dev"
    assert "NEW_VAR" not in os.environ


def test_unset_with_none():
    with temp_env(MODE=None):
        assert "MODE" not in os.environ
    assert os.environ["MODE"] == "dev"


def test_restore_on_exception():
    with pytest.raises(ZeroDivisionError):
        with temp_env(MODE="x"):
            1 / 0
    assert os.environ["MODE"] == "dev"

"""Step 1 checks. Runs with the current directory = the learner's project folder."""

from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from copilot.llm import DEFAULT_MODEL, ask, get_client

ROOT = Path.cwd()


class FakeClient:
    def __init__(self, text="Hello there!"):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(role="assistant", content=self.text), finish_reason="stop")])


def test_groq_is_a_dependency():
    text = (ROOT / "pyproject.toml").read_text()
    assert "groq" in text, "run `uv add groq` so it is listed in pyproject.toml"


def test_package_exists():
    assert (ROOT / "copilot" / "__init__.py").exists(), "create copilot/__init__.py"


def test_env_file_is_ignored():
    lines = [line.strip() for line in (ROOT / ".gitignore").read_text().splitlines()]
    assert ".env" in lines, "add a line `.env` to .gitignore so your real key is never committed"


def test_env_example_has_no_real_key():
    example = ROOT / ".env.example"
    assert example.exists(), "create .env.example that lists GROQ_API_KEY"
    text = example.read_text()
    assert "GROQ_API_KEY" in text, ".env.example should name GROQ_API_KEY"
    for line in text.splitlines():
        if line.startswith("GROQ_API_KEY="):
            value = line.split("=", 1)[1].strip()
            assert not (value.startswith("gsk_") and len(value) > 20), "never put a real key in .env.example"


def test_get_client_fails_clearly_without_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    with pytest.raises(RuntimeError) as info:
        get_client()
    assert "GROQ_API_KEY" in str(info.value), "the error message should name GROQ_API_KEY"


def test_get_client_with_key(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key_for_checkpoint")
    client = get_client()
    assert hasattr(client, "chat"), "get_client() should return the Groq client"


def test_ask_sends_one_user_message():
    client = FakeClient("Hello there!")
    assert ask(client, "Hi") == "Hello there!"
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["messages"] == [{"role": "user", "content": "Hi"}]
    assert call["model"] == DEFAULT_MODEL


def test_ask_custom_model():
    client = FakeClient()
    ask(client, "Hi", model="llama-3.3-70b-versatile")
    assert client.calls[0]["model"] == "llama-3.3-70b-versatile"

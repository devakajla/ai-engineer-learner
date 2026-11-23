from types import SimpleNamespace as NS

import pytest

from solution import safe_ask


class FakeClient:
    def __init__(self, text="Hello!", finish="stop"):
        self.text = text
        self.finish = finish
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(
            choices=[NS(message=NS(role="assistant", content=self.text), finish_reason=self.finish)],
            usage=NS(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )


def test_normal_call():
    client = FakeClient()
    result = safe_ask(client, "Hi", "chat", (0.5, 1.5), 4096)
    assert result["ok"] is True
    assert result["reply"] == "Hello!"
    assert result["usage"] == {"input": 100, "output": 50, "total": 150}
    assert result["cost"] == round(100 / 1e6 * 0.5 + 50 / 1e6 * 1.5, 6)
    assert result["cut_off"] is False
    call = client.calls[0]
    assert call["messages"] == [{"role": "user", "content": "Hi"}]
    assert call["temperature"] == 0.7 and call["max_completion_tokens"] == 500


def test_too_long_makes_no_call():
    client = FakeClient()
    result = safe_ask(client, "a" * 20000, "chat", (0.5, 1.5), 4096)
    assert result == {"ok": False, "reason": "too long"}
    assert client.calls == [], "do not call the model when the prompt does not fit"


def test_exact_fit_is_allowed():
    client = FakeClient()
    # 3596 tokens (14384 chars) + 500 output = 4096
    result = safe_ask(client, "a" * (3596 * 4), "chat", (0.5, 1.5), 4096)
    assert result["ok"] is True


def test_cut_off_is_reported():
    client = FakeClient(finish="length")
    assert safe_ask(client, "Hi", "extract", (1, 1), 4096)["cut_off"] is True
    assert client.calls[0]["max_completion_tokens"] == 200


def test_unknown_task():
    with pytest.raises(ValueError, match="unknown task: poem"):
        safe_ask(FakeClient(), "Hi", "poem", (1, 1), 4096)

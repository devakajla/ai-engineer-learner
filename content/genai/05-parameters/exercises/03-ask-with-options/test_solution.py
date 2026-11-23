from types import SimpleNamespace as NS

from solution import ask_with


class FakeClient:
    def __init__(self, text="blue"):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(role="assistant", content=self.text))])


def test_returns_text_and_sends_settings():
    client = FakeClient("blue")
    assert ask_with(client, "Name a colour.", temperature=0, max_output_tokens=5) == "blue"
    call = client.calls[0]
    assert call["model"] == "qwen/qwen3.8-27b"
    assert call["messages"] == [{"role": "user", "content": "Name a colour."}]
    assert call["temperature"] == 0
    assert call["max_completion_tokens"] == 5, "send the limit as max_completion_tokens"


def test_defaults():
    client = FakeClient()
    ask_with(client, "Hi")
    call = client.calls[0]
    assert call["temperature"] == 0.7
    assert call["max_completion_tokens"] == 500


def test_stop_only_when_given():
    client = FakeClient()
    ask_with(client, "Hi")
    assert "stop" not in client.calls[0], "do not send stop when it is None"
    ask_with(client, "List 3 fruits.", stop="END")
    assert client.calls[1]["stop"] == "END"

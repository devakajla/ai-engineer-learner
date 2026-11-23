from types import SimpleNamespace as NS

from solution import ask


class FakeClient:
    """Works like the Groq client, but returns a fixed answer and records the calls."""

    def __init__(self, text="It is 4."):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        message = NS(role="assistant", content=self.text)
        return NS(choices=[NS(message=message, finish_reason="stop")])


def test_returns_the_answer_text():
    client = FakeClient("It is 4.")
    assert ask(client, "What is 2+2?") == "It is 4."


def test_sends_one_user_message():
    client = FakeClient()
    ask(client, "What is 2+2?")
    assert len(client.calls) == 1, "call create exactly once"
    call = client.calls[0]
    assert call["messages"] == [{"role": "user", "content": "What is 2+2?"}]
    assert call["model"] == "qwen/qwen3.8-27b", "use the default model"


def test_custom_model():
    client = FakeClient()
    ask(client, "Hi", model="llama-3.3-70b-versatile")
    assert client.calls[0]["model"] == "llama-3.3-70b-versatile"

from types import SimpleNamespace as NS

from solution import ask_json


class FakeClient:
    def __init__(self, text):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(role="assistant", content=self.text))])


def test_returns_the_data():
    client = FakeClient('{"name": "Dev", "age": 30}')
    assert ask_json(client, "Give name and age of Dev, 30") == {"name": "Dev", "age": 30}


def test_bad_json_gives_none():
    assert ask_json(FakeClient("Hello!"), "Hi") is None


def test_the_call():
    client = FakeClient("{}")
    ask_json(client, "Q?")
    call = client.calls[0]
    assert call["response_format"] == {"type": "json_object"}, "turn on JSON mode"
    assert call["temperature"] == 0
    assert call["model"] == "qwen/qwen3.8-27b"
    assert call["messages"] == [
        {"role": "system", "content": "Reply with JSON only."},
        {"role": "user", "content": "Q?"},
    ]

from types import SimpleNamespace as NS


class FakeClient:
    def __init__(self, text):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content=self.text))])

from solution import choose_source

SOURCES = {"api": "REST API docs", "hr": "HR policies"}


def test_clean_reply():
    assert choose_source(FakeClient("  HR.\n"), "How do I take leave?", SOURCES) == "hr"


def test_none_and_unknown():
    assert choose_source(FakeClient("none"), "weather?", SOURCES) is None
    assert choose_source(FakeClient("finance"), "tax?", SOURCES) is None
    assert choose_source(FakeClient("I think api"), "x", SOURCES) is None


def test_call_shape():
    client = FakeClient("api")
    choose_source(client, "How to login?", SOURCES)
    call = client.calls[0]
    assert call["temperature"] == 0
    assert call["messages"][1] == {"role": "user", "content": "How to login?"}
    system = call["messages"][0]["content"]
    assert call["messages"][0]["role"] == "system"
    assert "api: REST API docs" in system and "hr: HR policies" in system

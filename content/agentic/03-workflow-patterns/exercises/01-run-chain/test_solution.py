from types import SimpleNamespace as NS


class FakeClient:
    """Returns the replies one by one (the last one repeats). Records every call."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        index = min(len(self.calls) - 1, len(self.replies) - 1)
        return NS(choices=[NS(message=NS(content=self.replies[index]))])


def user_text(call):
    return call["messages"][-1]["content"]


def system_text(call):
    first = call["messages"][0]
    return first["content"] if first["role"] == "system" else None

from solution import run_chain


def test_each_step_gets_the_previous_reply():
    client = FakeClient("English text", "Short text")
    steps = ["Translate: {input}", "Shorten: {input}"]
    out = run_chain(client, steps, "Bonjour")
    assert out == {"result": "Short text", "outputs": ["English text", "Short text"]}
    assert [user_text(c) for c in client.calls] == ["Translate: Bonjour", "Shorten: English text"]


def test_temperature_zero_and_no_system_message():
    client = FakeClient("a")
    run_chain(client, ["{input}"], "x")
    assert client.calls[0]["temperature"] == 0 and system_text(client.calls[0]) is None


def test_replies_are_stripped():
    client = FakeClient("  padded \n", "end")
    assert run_chain(client, ["{input}", "{input}"], "x")["outputs"] == ["padded", "end"]
    assert user_text(client.calls[1]) == "padded"


def test_no_steps():
    client = FakeClient("never")
    assert run_chain(client, [], "hello") == {"result": "hello", "outputs": []}
    assert client.calls == []


def test_marker_can_appear_twice_or_be_missing():
    client = FakeClient("r1", "r2")
    run_chain(client, ["{input} and {input}", "fixed prompt"], "x")
    assert user_text(client.calls[0]) == "x and x" and user_text(client.calls[1]) == "fixed prompt"


def test_braces_in_the_text_are_safe():
    client = FakeClient("ok")
    run_chain(client, ["Fix: {input}"], "{'a': 1}")
    assert user_text(client.calls[0]) == "Fix: {'a': 1}"

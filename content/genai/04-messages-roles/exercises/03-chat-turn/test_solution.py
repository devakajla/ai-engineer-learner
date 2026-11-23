from types import SimpleNamespace as NS

from solution import chat_turn


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        # Save a copy of the messages, so later changes cannot hide what was sent.
        self.calls.append({"model": kwargs["model"], "messages": list(kwargs["messages"])})
        text = self.replies.pop(0)
        return NS(choices=[NS(message=NS(role="assistant", content=text))])


def test_first_turn():
    client = FakeClient(["Hello!"])
    reply, history = chat_turn(client, [], "Hi")
    assert reply == "Hello!"
    assert history == [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    assert client.calls[0]["messages"] == [{"role": "user", "content": "Hi"}]
    assert client.calls[0]["model"] == "qwen/qwen3.8-27b"


def test_second_turn_sends_the_history():
    client = FakeClient(["Hello!", "You're welcome."])
    _, history = chat_turn(client, [], "Hi")
    reply, history = chat_turn(client, history, "Thanks")
    assert reply == "You're welcome."
    assert [m["content"] for m in client.calls[1]["messages"]] == ["Hi", "Hello!", "Thanks"], (
        "the second call must send the old turns plus the new question"
    )
    assert len(history) == 4


def test_does_not_change_the_input_history():
    client = FakeClient(["ok"])
    old = [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"}]
    chat_turn(client, old, "c")
    assert len(old) == 2, "do not change the history that was passed in"


def test_custom_model():
    client = FakeClient(["ok"])
    chat_turn(client, [], "Hi", model="llama-3.3-70b-versatile")
    assert client.calls[0]["model"] == "llama-3.3-70b-versatile"

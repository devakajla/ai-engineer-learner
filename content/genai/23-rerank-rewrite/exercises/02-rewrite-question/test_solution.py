from types import SimpleNamespace as NS

from solution import rewrite_question


class FakeClient:
    def __init__(self, reply="  How do I undo deleting a task?\n"):
        self.reply = reply
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content=self.reply))])


HISTORY = [
    {"role": "user", "content": "How do I delete a task?"},
    {"role": "assistant", "content": "Use the DELETE endpoint."},
]


def test_rewrite():
    client = FakeClient()
    out = rewrite_question(client, HISTORY, "And how do I undo it?")
    assert out == "How do I undo deleting a task?"
    call = client.calls[0]
    assert call["temperature"] == 0 and call["max_completion_tokens"] == 100
    content = call["messages"][0]["content"]
    assert content == (
        "Rewrite the last question so it can be understood without the chat. Reply with the question only.\n\n"
        "Chat:\nuser: How do I delete a task?\nassistant: Use the DELETE endpoint.\n\n"
        "Last question: And how do I undo it?"
    )


def test_no_history_no_call():
    client = FakeClient()
    assert rewrite_question(client, [], "What is a task?") == "What is a task?"
    assert client.calls == []

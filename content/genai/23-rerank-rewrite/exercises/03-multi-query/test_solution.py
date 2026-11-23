from types import SimpleNamespace as NS

from solution import multi_query


class FakeClient:
    def __init__(self, reply):
        self.reply = reply
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content=self.reply))])


def test_clean_and_dedupe():
    reply = "- How can I remove a task?\n- Steps to delete a task\n\n- how do i delete a task?"
    client = FakeClient(reply)
    out = multi_query(client, "How do I delete a task?", n=3)
    assert out == ["How do I delete a task?", "How can I remove a task?", "Steps to delete a task"]
    call = client.calls[0]
    assert call["temperature"] == 0.7 and call["max_completion_tokens"] == 200
    assert call["messages"][0]["content"] == (
        "Write 3 different ways to ask this question, one per line, no numbering:\nHow do I delete a task?"
    )


def test_limit_n():
    client = FakeClient("a\nb\nc\nd")
    assert multi_query(client, "q", n=2) == ["q", "a", "b"]


def test_bullets_and_spaces():
    client = FakeClient("  * one  \n\u2022 two\n   \n-three")
    assert multi_query(client, "q", n=5) == ["q", "one", "two", "three"]


def test_duplicates_removed():
    client = FakeClient("a\nA\nb\na")
    assert multi_query(client, "q", n=5) == ["q", "a", "b"]


def test_empty_reply():
    assert multi_query(FakeClient(""), "q") == ["q"]

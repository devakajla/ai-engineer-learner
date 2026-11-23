from types import SimpleNamespace as NS


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        text = self.replies.pop(0) if self.replies else ""
        return NS(choices=[NS(message=NS(content=text))])

from solution import judge


def test_first_try():
    client = FakeClient(['{"score": 5, "reason": "ok"}'])
    assert judge(client, "Q?", "ctx", "A.") == {"score": 5, "reason": "ok"}
    assert len(client.calls) == 1


def test_call_settings():
    client = FakeClient(['{"score": 5}'])
    judge(client, "Q?", "ctx", "A.")
    call = client.calls[0]
    assert call["temperature"] == 0
    assert call["messages"][0]["role"] == "system"
    assert "<answer>\nA.\n</answer>" in call["messages"][1]["content"]


def test_retry_then_ok():
    client = FakeClient(["I think it is fine", '{"score": 2, "reason": "weak"}'])
    assert judge(client, "Q?", "ctx", "A.")["score"] == 2
    assert len(client.calls) == 2


def test_gives_up():
    client = FakeClient(["bad", "worse", '{"score": 5}'])
    assert judge(client, "Q?", "ctx", "A.", max_tries=2) == {"score": None, "reason": "unparseable"}
    assert len(client.calls) == 2


def test_max_tries_one():
    client = FakeClient(["bad", '{"score": 5}'])
    judge(client, "Q?", "ctx", "A.", max_tries=1)
    assert len(client.calls) == 1

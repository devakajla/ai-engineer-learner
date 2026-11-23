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

from solution import improve_loop


def test_accepted_at_once():
    client = FakeClient("draft 1", "OK")
    assert improve_loop(client, "slogan") == {"text": "draft 1", "rounds": 0, "accepted": True}
    assert len(client.calls) == 2


def test_one_revision():
    client = FakeClient("v1", "Too long.", "v2", "OK.")
    assert improve_loop(client, "slogan") == {"text": "v2", "rounds": 1, "accepted": True}
    assert len(client.calls) == 4


def test_prompts():
    client = FakeClient("v1", "Too long.", "v2", "ok")
    improve_loop(client, "T")
    assert user_text(client.calls[0]) == "T"
    assert user_text(client.calls[1]) == (
        "Task: T\n\nDraft:\nv1\n\n"
        "If the draft is good, reply exactly OK. Otherwise reply with one short sentence of feedback."
    )
    assert user_text(client.calls[2]) == (
        "Task: T\n\nDraft:\nv1\n\nFeedback: Too long.\n\n"
        "Rewrite the draft to fix the feedback. Reply with the new draft only."
    )
    assert "Draft:\nv2" in user_text(client.calls[3]), "the new draft is the one that gets evaluated"


def test_gives_up_after_max_rounds():
    client = FakeClient("v1", "bad", "v2", "bad", "v3", "bad")
    out = improve_loop(client, "T", max_rounds=2)
    assert out == {"text": "v3", "rounds": 2, "accepted": False}
    assert len(client.calls) == 6


def test_zero_rounds_never_revises():
    client = FakeClient("v1", "bad")
    assert improve_loop(client, "T", max_rounds=0) == {"text": "v1", "rounds": 0, "accepted": False}
    assert len(client.calls) == 2


def test_ok_must_be_exact():
    client = FakeClient("v1", "OK but shorter please", "v2", "OK")
    out = improve_loop(client, "T")
    assert out["accepted"] and out["text"] == "v2" and out["rounds"] == 1
    assert "Feedback: OK but shorter please" in user_text(client.calls[2])


def test_lowercase_ok_is_accepted():
    assert improve_loop(FakeClient("v1", "ok"), "T")["accepted"] is True

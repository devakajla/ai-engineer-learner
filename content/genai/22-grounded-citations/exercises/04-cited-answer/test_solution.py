from types import SimpleNamespace as NS

from solution import cited_answer


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        text = self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]
        return NS(choices=[NS(message=NS(content=text))])


HITS = [
    {"id": "a", "text": "Use DELETE.", "source": "tasks.md", "heading": "Delete", "score": 0.9},
    {"id": "b", "text": "Send a token.", "source": "auth.md", "heading": "", "score": 0.8},
]


def retrieve(question, k):
    return HITS[:k]


def test_good_first_time():
    client = FakeClient(["Use DELETE [1]."])
    out = cited_answer(client, retrieve, "How?")
    assert out["ok"] is True and out["answer"] == "Use DELETE [1]."
    assert out["sources"] == [{"n": 1, "source": "tasks.md", "heading": "Delete"}]
    assert len(client.calls) == 1
    assert "cite the context number" in client.calls[0]["messages"][0]["content"]


def test_repair_once():
    client = FakeClient(["Use DELETE.", "Use DELETE [1]."])
    out = cited_answer(client, retrieve, "How?")
    assert out["ok"] is True and len(client.calls) == 2
    second = client.calls[1]["messages"]
    assert second[-2] == {"role": "assistant", "content": "Use DELETE."}
    assert "numbers 1 to 2" in second[-1]["content"]
    assert len(client.calls[0]["messages"]) == 2, "first call keeps only system and user"


def test_invalid_number_is_repaired():
    client = FakeClient(["Use DELETE [5].", "Use DELETE [2]."])
    out = cited_answer(client, retrieve, "How?")
    assert out["ok"] is True and out["sources"][0]["source"] == "auth.md"


def test_gives_up_after_two():
    client = FakeClient(["no cite"])
    out = cited_answer(client, retrieve, "How?")
    assert out == {"answer": "no cite", "sources": [], "ok": False}
    assert len(client.calls) == 2


def test_dont_know_is_fine():
    client = FakeClient(["I don't know."])
    out = cited_answer(client, retrieve, "How?")
    assert out == {"answer": "I don't know.", "sources": [], "ok": True}
    assert len(client.calls) == 1


def test_no_hits_no_call():
    client = FakeClient(["x"])
    out = cited_answer(client, lambda q, k: [], "How?")
    assert out == {"answer": "I don't know.", "sources": [], "ok": True}
    assert client.calls == []

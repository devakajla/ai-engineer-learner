from types import SimpleNamespace as NS

from solution import answer


class FakeClient:
    def __init__(self, reply="Use DELETE [1]."):
        self.reply = reply
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        return NS(choices=[NS(message=NS(content=self.reply))])


HITS = [
    {"id": "a", "text": "Use DELETE.", "source": "tasks.md", "heading": "Delete", "score": 0.9},
    {"id": "b", "text": "Other.", "source": "x.md", "heading": "", "score": 0.3},
]


def retrieve(question, k):
    return HITS[:k]


def test_answer():
    client = FakeClient()
    out = answer(client, retrieve, "How do I delete?", k=2)
    assert out["answer"] == "Use DELETE [1]."
    assert out["hits"] == HITS
    call = client.calls[0]
    assert call["temperature"] == 0 and call["max_completion_tokens"] == 300
    assert "[1] tasks.md > Delete" in call["messages"][1]["content"]


def test_min_score_filters():
    client = FakeClient()
    out = answer(client, retrieve, "q", k=2, min_score=0.5)
    assert [h["id"] for h in out["hits"]] == ["a"]
    assert "[2]" not in client.calls[0]["messages"][1]["content"]


def test_nothing_found_no_call():
    client = FakeClient()
    out = answer(client, lambda q, k: [], "pizza?")
    assert out == {"answer": "I don't know.", "hits": []}
    assert client.calls == []


def test_all_below_threshold_no_call():
    client = FakeClient()
    out = answer(client, retrieve, "q", k=2, min_score=0.95)
    assert out["hits"] == [] and client.calls == []


def test_k_is_passed():
    seen = []

    def spy(question, k):
        seen.append(k)
        return HITS

    answer(FakeClient(), spy, "q", k=7)
    assert seen == [7]

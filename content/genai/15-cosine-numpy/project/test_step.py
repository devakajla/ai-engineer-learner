"""Step 8 checks. Runs with the current directory = the learner's project folder."""

import pytest

from copilot.llm import chat_turn
from copilot.search import search_texts
from copilot.similarity import cosine_scores, cosine_similarity, top_k
from types import SimpleNamespace as NS


class FakeClient:
    def __init__(self):
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        message = NS(role="assistant", content="ok", tool_calls=None)
        return NS(choices=[NS(message=message, finish_reason="stop")])


class Embed:
    """Fake embedder: [count of 'task', count of 'login']. Records calls."""

    def __init__(self):
        self.calls = []

    def __call__(self, texts):
        self.calls.append(list(texts))
        return [[t.count("task"), t.count("login")] for t in texts]


def test_earlier_steps_still_work():
    assert chat_turn(FakeClient(), [], "Hello")[0] == "ok"


def test_cosine_similarity():
    assert cosine_similarity([1, 0], [1, 1]) == pytest.approx(0.7071067811865475)
    assert cosine_similarity([1, 1], [10, 10]) == pytest.approx(1.0)
    assert cosine_similarity([0, 0], [1, 2]) == 0.0, "a zero vector must give 0.0, not nan"
    with pytest.raises(ValueError):
        cosine_similarity([1, 2], [1, 2, 3])


def test_cosine_scores():
    assert cosine_scores([1, 0], []) == []
    scores = cosine_scores([1, 0], [[1, 0], [0, 1], [0, 0]])
    assert scores == [pytest.approx(1.0), pytest.approx(0.0), 0.0]
    assert all(type(s) is float for s in scores)


def test_top_k():
    matrix = [[1, 0], [0, 1], [1, 1]]
    assert [i for i, _ in top_k([1, 0], matrix, 2)] == [0, 2]
    assert [i for i, _ in top_k([1, 0], matrix, 99)] == [0, 2, 1]
    assert top_k([1, 0], matrix, 0) == [] and top_k([1, 0], [], 3) == []
    same = [[1, 0], [2, 0]]
    assert [i for i, _ in top_k([1, 0], same, 2)] == [0, 1], "ties: lower index first"
    assert type(top_k([1, 0], matrix, 1)[0][0]) is int


def test_search_texts_returns_dicts_best_first():
    docs = ["delete a task", "login with a token", "list every task and task"]
    embed = Embed()
    hits = search_texts("login", docs, k=2, embed=embed)
    assert hits[0]["text"] == "login with a token" and hits[0]["index"] == 1
    assert set(hits[0]) == {"index", "text", "score"}
    assert len(hits) == 2


def test_search_texts_embeds_in_batches_and_handles_edges():
    docs = ["a task", "a login"]
    embed = Embed()
    search_texts("task", docs, embed=embed)
    assert embed.calls == [docs, ["task"]], "embed all texts in one call, then the query"
    empty = Embed()
    assert search_texts("task", [], embed=empty) == [] and empty.calls == []
    assert search_texts("task", docs, k=0, embed=Embed()) == []

import pytest

from solution import search_texts


class Embed:
    """A fake embedder: [count of 'task', count of 'login'] and it records its calls."""

    def __init__(self):
        self.calls = []

    def __call__(self, texts):
        self.calls.append(list(texts))
        return [[t.count("task"), t.count("login")] for t in texts]


DOCS = ["delete a task", "login with a token", "list every task and task"]


def test_examples():
    embed = Embed()
    result = search_texts(embed, "task", DOCS, k=2)
    assert [t for t, _ in result] == ["delete a task", "list every task and task"]
    assert all(score == pytest.approx(1.0) for _, score in result)
    assert search_texts(Embed(), "login", DOCS, k=1)[0][0] == "login with a token"


def test_embeds_in_batches():
    embed = Embed()
    search_texts(embed, "task", DOCS)
    assert embed.calls == [DOCS, ["task"]], "embed all texts in ONE call, then the query in one call"


def test_edges():
    embed = Embed()
    assert search_texts(embed, "task", [], k=3) == []
    assert embed.calls == [], "no texts: do not call embed at all"
    assert search_texts(Embed(), "task", DOCS, k=0) == []
    assert len(search_texts(Embed(), "task", DOCS, k=99)) == 3


def test_order_and_ties():
    docs = ["a task", "a login", "task login"]
    result = search_texts(Embed(), "task", docs, k=3)
    assert [t for t, _ in result] == ["a task", "task login", "a login"]
    assert result[2][1] == 0.0

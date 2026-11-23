from solution import rerank


def overlap(question, text):
    return len(set(question.split()) & set(text.split()))


HITS = [
    {"id": "a", "text": "weather today"},
    {"id": "b", "text": "delete a task"},
    {"id": "c", "text": "task"},
]


def test_best_first():
    out = rerank(overlap, "delete task", HITS, 3)
    assert [h["id"] for h in out] == ["b", "c", "a"]
    assert out[0]["rerank_score"] == 2


def test_top_n():
    assert [h["id"] for h in rerank(overlap, "delete task", HITS, 1)] == ["b"]


def test_ties_keep_order():
    out = rerank(lambda q, t: 1, "q", HITS, 3)
    assert [h["id"] for h in out] == ["a", "b", "c"]


def test_zero_and_empty():
    assert rerank(overlap, "q", HITS, 0) == []
    assert rerank(overlap, "q", [], 3) == []


def test_originals_untouched():
    rerank(overlap, "delete task", HITS, 3)
    assert "rerank_score" not in HITS[0]


def test_keeps_other_keys():
    hits = [{"id": "x", "text": "t", "source": "s.md"}]
    assert rerank(lambda q, t: 5, "q", hits, 1)[0]["source"] == "s.md"

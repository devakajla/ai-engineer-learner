from solution import hybrid_search

DOCS = ["error E1042 means bad token", "how to log in", "delete a task"]


def test_exact_code_wins_by_keyword():
    out = hybrid_search("E1042", DOCS, [0.1, 0.8, 0.2], k=3)
    assert out[0][0] == "error E1042 means bad token"
    assert len(out) == 3


def test_both_agree_goes_first():
    out = hybrid_search("log in", DOCS, [0.1, 0.9, 0.2], k=1)
    assert out[0][0] == "how to log in"


def test_k_and_empty():
    assert hybrid_search("x", DOCS, [0, 0, 0], k=0) == []
    assert hybrid_search("x", [], [], k=3) == []
    assert len(hybrid_search("log", DOCS, [0.1, 0.9, 0.2], k=2)) == 2


def test_no_keyword_match_uses_vector_only():
    out = hybrid_search("pizza", DOCS, [0.1, 0.9, 0.5], k=3)
    assert [d for d, _ in out] == ["how to log in", "delete a task", "error E1042 means bad token"]


def test_scores_are_floats_and_descending():
    out = hybrid_search("task", DOCS, [0.1, 0.2, 0.9], k=3)
    scores = [s for _, s in out]
    assert scores == sorted(scores, reverse=True)
    assert all(isinstance(s, float) for s in scores)

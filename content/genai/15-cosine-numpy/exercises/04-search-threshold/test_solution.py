from solution import search_with_threshold


def embed(texts):
    return [[t.count("task"), t.count("login")] for t in texts]


DOCS = ["delete a task", "login with a token", "weather today"]


def test_keeps_good_hits():
    assert search_with_threshold(embed, "task", DOCS, k=3, min_score=0.5) == [("delete a task", 1.0)]


def test_nothing_close():
    assert search_with_threshold(embed, "pizza", DOCS, k=3, min_score=0.5) == []


def test_default_keeps_all_up_to_k():
    out = search_with_threshold(embed, "task", DOCS, k=2)
    assert len(out) == 2


def test_k_zero_and_empty():
    assert search_with_threshold(embed, "task", DOCS, k=0) == []
    assert search_with_threshold(embed, "task", [], k=3, min_score=0.1) == []


def test_boundary_is_kept():
    assert search_with_threshold(embed, "login", DOCS, k=1, min_score=1.0) == [("login with a token", 1.0)]

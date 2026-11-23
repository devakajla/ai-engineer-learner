import pytest

from solution import reciprocal_rank_fusion


def test_examples():
    result = reciprocal_rank_fusion([["a", "b", "c"], ["c", "a", "d"]])
    assert [item for item, _ in result] == ["a", "c", "b", "d"]
    scores = dict(result)
    assert scores["a"] == pytest.approx(1 / 61 + 1 / 62)
    assert scores["c"] == pytest.approx(1 / 63 + 1 / 61)
    assert scores["b"] == pytest.approx(1 / 62)
    assert scores["d"] == pytest.approx(1 / 63)
    assert reciprocal_rank_fusion([["x"], ["y"]], k=1) == [("x", 0.5), ("y", 0.5)]


def test_items_in_both_lists_beat_items_in_one():
    result = reciprocal_rank_fusion([["a", "b", "c", "d"], ["d", "x", "y", "z"]])
    assert result[0][0] == "d", "d is in both lists, so it wins even though it is last in one of them"


def test_edges():
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []
    assert reciprocal_rank_fusion([["a", "b"]]) == [("a", pytest.approx(1 / 61)), ("b", pytest.approx(1 / 62))]


def test_ties_keep_first_seen_order():
    result = reciprocal_rank_fusion([["a", "b"], ["b", "a"]])
    assert [item for item, _ in result] == ["a", "b"], "equal scores: a was seen first"


def test_k_changes_the_scores():
    low = dict(reciprocal_rank_fusion([["a", "b"]], k=1))
    assert low["a"] == pytest.approx(1 / 2) and low["b"] == pytest.approx(1 / 3)

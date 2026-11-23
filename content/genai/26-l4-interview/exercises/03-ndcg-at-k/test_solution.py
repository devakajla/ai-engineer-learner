import math

from solution import ndcg_at_k


def test_perfect_order():
    assert abs(ndcg_at_k([3, 2, 0], 3) - 1.0) < 1e-9


def test_bad_order():
    dcg = 0 / math.log2(2) + 2 / math.log2(3) + 3 / math.log2(4)
    ideal = 3 / math.log2(2) + 2 / math.log2(3) + 0
    assert abs(ndcg_at_k([0, 2, 3], 3) - dcg / ideal) < 1e-9


def test_k_cuts_both():
    expected = (1 / math.log2(2)) / (3 / math.log2(2))
    assert abs(ndcg_at_k([1, 3, 3], 1) - expected) < 1e-9


def test_no_relevance_and_edges():
    assert ndcg_at_k([0, 0], 2) == 0.0
    assert ndcg_at_k([], 3) == 0.0
    assert ndcg_at_k([3], 0) == 0.0


def test_ideal_uses_all_grades():
    assert ndcg_at_k([0, 0, 3], 2) == 0.0
    assert ndcg_at_k([1, 3], 2) < 1.0

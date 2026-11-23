import pytest

from solution import recall_at_k


def test_examples():
    assert recall_at_k(["a", "c", "x", "d"], ["a", "b", "c", "d"], 4) == 0.75
    assert recall_at_k(["a", "b"], ["a", "b", "c"], 2) == 1.0
    assert recall_at_k(["x", "y"], ["a", "b"], 2) == 0.0
    assert recall_at_k(["a"], [], 3) == 1.0


def test_only_the_first_k_count():
    assert recall_at_k(["x", "a"], ["a", "b"], 1) == 0.0, "'a' is second in found, outside the first 1"
    assert recall_at_k(["a", "b", "c"], ["c", "a", "b"], 2) == 0.5, "truth[:2] = c, a; found[:2] = a, b"


def test_order_inside_k_does_not_matter():
    assert recall_at_k(["b", "a"], ["a", "b"], 2) == 1.0


def test_short_lists_and_float():
    assert recall_at_k([], ["a", "b"], 2) == 0.0
    assert recall_at_k(["a"], ["a"], 10) == 1.0
    assert type(recall_at_k(["a"], ["a"], 1)) is float


def test_bad_k():
    for k in (0, -1):
        with pytest.raises(ValueError):
            recall_at_k(["a"], ["a"], k)

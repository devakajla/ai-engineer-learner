from solution import count_pairs


def test_examples():
    assert count_pairs([1, 2, 3, 4], 5) == 2
    assert count_pairs([2, 2, 2], 4) == 3


def test_edges():
    assert count_pairs([], 3) == 0
    assert count_pairs([5], 5) == 0, "one item has no pair"
    assert count_pairs([1, 2], 10) == 0
    assert count_pairs([0, 0, 0, 0], 0) == 6
    assert count_pairs([-1, 1, 0, 2, -2], 0) == 2

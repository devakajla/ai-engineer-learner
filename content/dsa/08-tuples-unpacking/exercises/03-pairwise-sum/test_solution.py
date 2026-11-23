from solution import pairwise_sum


def test_examples():
    assert pairwise_sum([1, 2, 3], [10, 20, 30]) == [11, 22, 33]
    assert pairwise_sum([1, 2, 3], [5]) == [6]


def test_more():
    assert pairwise_sum([], [1]) == []
    assert pairwise_sum([-1, 1], [1, -1]) == [0, 0]

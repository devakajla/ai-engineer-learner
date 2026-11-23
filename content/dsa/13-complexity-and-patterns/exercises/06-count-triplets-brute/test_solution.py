from solution import count_triplets


def test_examples():
    assert count_triplets([1, 2, 3, 4, 5], 9) == 2
    assert count_triplets([0, 0, 0, 0], 0) == 4


def test_edges():
    assert count_triplets([], 0) == 0
    assert count_triplets([1, 2], 3) == 0, "fewer than 3 items"
    assert count_triplets([1, 2, 3], 6) == 1
    assert count_triplets([-1, 0, 1, 2, -1, -4], 0) == 3
    assert count_triplets([5, 5, 5, 5, 5], 15) == 10

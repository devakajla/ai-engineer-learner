from solution import intersect_counts


def test_examples():
    assert intersect_counts([1, 2, 2, 1], [2, 2]) == [2, 2]
    assert intersect_counts([4, 9, 5], [9, 4, 9, 8, 4]) == [4, 9]
    assert intersect_counts([1], [2]) == []


def test_more():
    assert intersect_counts([], [1]) == []
    assert intersect_counts([1, 1, 1], [1, 1]) == [1, 1]
    assert intersect_counts([3, 3], [3, 3, 3]) == [3, 3]

from solution import prefix_sums


def test_examples():
    assert prefix_sums([1, 2, 3, 4]) == [1, 3, 6, 10]
    assert prefix_sums([]) == []


def test_more():
    assert prefix_sums([5]) == [5]
    assert prefix_sums([3, -3, 3]) == [3, 0, 3]
    assert prefix_sums([0, 0]) == [0, 0]

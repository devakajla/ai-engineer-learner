from solution import second_largest


def test_examples():
    assert second_largest([3, 1, 4, 1, 5]) == 4
    assert second_largest([7, 7, 7]) is None
    assert second_largest([2]) is None


def test_more():
    assert second_largest([]) is None
    assert second_largest([1, 2]) == 1
    assert second_largest([5, 4, 3]) == 4
    assert second_largest([-1, -5, -3]) == -3
    assert second_largest([5, 5, 4]) == 4

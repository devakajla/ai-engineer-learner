from solution import closest_to_zero


def test_examples():
    assert closest_to_zero([4, -2, 7]) == (-2, 2)
    assert closest_to_zero([-3, 3, 5]) == (3, 3)
    assert closest_to_zero([0, 5]) == (0, 0)


def test_more():
    assert closest_to_zero([5]) == (5, 5)
    assert closest_to_zero([3, -3]) == (3, 3)
    assert closest_to_zero([-1, -2]) == (-1, 1)

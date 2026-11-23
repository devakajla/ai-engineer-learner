from solution import min_max


def test_examples():
    assert min_max([4, 1, 9]) == (1, 9)
    assert min_max([5]) == (5, 5)


def test_more():
    assert min_max([-3, -1, -2]) == (-3, -1)
    assert min_max([2, 2, 2]) == (2, 2)
    assert isinstance(min_max([1, 2]), tuple), "return a tuple"

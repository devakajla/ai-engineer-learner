from solution import min_max


def test_examples():
    assert min_max([3, 9, 1, 4]) == (1, 9)
    assert min_max([7]) == (7, 7)
    assert min_max([]) is None


def test_more():
    assert min_max([-5, -1, -9]) == (-9, -1)
    assert isinstance(min_max([1, 2]), tuple)

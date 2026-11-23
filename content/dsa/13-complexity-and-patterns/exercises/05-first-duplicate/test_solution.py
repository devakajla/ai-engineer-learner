from solution import first_duplicate


def test_examples():
    assert first_duplicate([2, 1, 3, 1, 2]) == 1
    assert first_duplicate([1, 2, 3]) is None


def test_edges():
    assert first_duplicate([]) is None
    assert first_duplicate([7]) is None
    assert first_duplicate([5, 5]) == 5
    assert first_duplicate([0, 1, 0]) == 0, "0 is a valid value, not 'nothing'"
    assert first_duplicate([3, 4, 5, 4, 3]) == 4
    assert first_duplicate(list(range(100000)) + [5]) == 5

from solution import rotate_right


def test_examples():
    assert rotate_right([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert rotate_right([1, 2, 3], 4) == [3, 1, 2]
    assert rotate_right([], 3) == []


def test_more():
    assert rotate_right([1, 2, 3], 0) == [1, 2, 3]
    assert rotate_right([1, 2, 3], 3) == [1, 2, 3]
    assert rotate_right([1], 10) == [1]

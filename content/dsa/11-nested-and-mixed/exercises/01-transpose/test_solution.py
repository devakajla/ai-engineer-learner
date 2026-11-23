from solution import transpose


def test_examples():
    assert transpose([[1, 2, 3], [4, 5, 6]]) == [[1, 4], [2, 5], [3, 6]]
    assert transpose([[7]]) == [[7]]


def test_more():
    assert transpose([[1, 2], [3, 4]]) == [[1, 3], [2, 4]]
    assert transpose([[1], [2], [3]]) == [[1, 2, 3]]
    assert transpose([[1, 2, 3]]) == [[1], [2], [3]]

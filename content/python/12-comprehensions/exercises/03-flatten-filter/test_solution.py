from solution import flatten_positive


def test_examples():
    assert flatten_positive([[1, -2], [3], [-4, 5]]) == [1, 3, 5]
    assert flatten_positive([[], [0, -1]]) == []


def test_more():
    assert flatten_positive([]) == []
    assert flatten_positive([[1.5, -1.5]]) == [1.5]
    assert flatten_positive([[3, 2], [1]]) == [3, 2, 1], "keep original order"

from solution import common


def test_examples():
    assert common([1, 2, 2, 3], [2, 3, 4]) == [2, 3]
    assert common(["x"], ["y"]) == []


def test_more():
    assert common([], [1]) == []
    assert common([3, 1, 2], [2, 1, 3]) == [1, 2, 3], "result must be sorted"
    assert isinstance(common([1], [1]), list)

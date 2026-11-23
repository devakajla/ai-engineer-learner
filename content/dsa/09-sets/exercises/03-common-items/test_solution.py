from solution import common_items


def test_examples():
    assert common_items([1, 2, 2, 3], [2, 3, 4]) == [2, 3]
    assert common_items([1], [2]) == []


def test_more():
    assert common_items([], [1, 2]) == []
    assert common_items([3, 1, 2], [2, 1, 3]) == [1, 2, 3]
    assert common_items(["b", "a"], ["a", "c"]) == ["a"]

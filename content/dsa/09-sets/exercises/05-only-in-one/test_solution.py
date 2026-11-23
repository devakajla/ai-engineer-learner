from solution import only_in_one


def test_examples():
    assert only_in_one([1, 2, 3], [2, 3, 4]) == [1, 4]
    assert only_in_one([1, 1], [1]) == []


def test_more():
    assert only_in_one([], [3, 1]) == [1, 3]
    assert only_in_one([5], []) == [5]
    assert only_in_one(["a", "b"], ["b", "c"]) == ["a", "c"]

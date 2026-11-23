from solution import most_common


def test_examples():
    assert most_common([1, 2, 2, 3, 3, 3]) == 3
    assert most_common(["a", "b", "b", "a"]) == "a"


def test_more():
    assert most_common([5]) == 5
    assert most_common([1, 2, 3]) == 1, "all tie: first wins"
    assert most_common([4, 4, 5, 5, 5, 4, 5]) == 5
    assert most_common(["x", "y", "y"]) == "y"

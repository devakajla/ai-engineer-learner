from solution import missing


def test_examples():
    assert missing([1, 3, 5], 5) == [2, 4]
    assert missing([1, 2, 3], 3) == []
    assert missing([], 3) == [1, 2, 3]


def test_more():
    assert missing([5, 5, 1], 5) == [2, 3, 4]
    assert missing([7, 8], 3) == [1, 2, 3], "numbers outside 1..n are ignored"
    assert missing([], 0) == []

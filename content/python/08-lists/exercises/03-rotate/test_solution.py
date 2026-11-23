from solution import rotate


def test_examples():
    assert rotate([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert rotate([1, 2, 3], 3) == [1, 2, 3]


def test_more():
    assert rotate([], 5) == []
    assert rotate([1, 2, 3], 0) == [1, 2, 3]
    assert rotate([1, 2, 3], 4) == [3, 1, 2], "k larger than the length wraps around"
    assert rotate([1], 10) == [1]
    original = [1, 2, 3]
    rotate(original, 1)
    assert original == [1, 2, 3], "do not change the input list"

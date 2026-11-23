from solution import has_duplicate


def test_examples():
    assert has_duplicate([1, 2, 3, 1]) is True
    assert has_duplicate([1, 2, 3]) is False


def test_more():
    assert has_duplicate([]) is False
    assert has_duplicate([5]) is False
    assert has_duplicate(["a", "b", "a"]) is True
    assert has_duplicate([0, False]) is True, "0 and False are equal in Python"

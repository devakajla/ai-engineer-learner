from solution import swap_ends


def test_examples():
    assert swap_ends((1, 2, 3, 4)) == (4, 2, 3, 1)
    assert swap_ends(("a", "b")) == ("b", "a")


def test_more():
    result = swap_ends((1, 2, 3))
    assert isinstance(result, tuple), "return a tuple, not a list"
    assert result == (3, 2, 1)
    assert swap_ends((5, 5)) == (5, 5)

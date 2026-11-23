from solution import is_even


def test_examples():
    assert is_even(4) is True
    assert is_even(7) is False


def test_edges():
    assert is_even(0) is True, "zero is even"
    assert is_even(-2) is True, "negative even"
    assert is_even(-3) is False, "negative odd"

from solution import thinking_share


def test_examples():
    assert thinking_share("a" * 400, 200) == 0.5
    assert thinking_share("", 50) == 0.0
    assert thinking_share("a" * 4000, 100) == 1.0
    assert thinking_share("abc", 0) == 0.0


def test_rounding():
    assert thinking_share("a" * 40, 30) == 0.33, "10 of 30 tokens is 0.33"


def test_returns_float():
    assert isinstance(thinking_share("a" * 8, 8), float)

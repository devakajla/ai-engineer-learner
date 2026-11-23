from solution import safe_divide


def test_examples():
    assert safe_divide(10, 4) == 2.5
    assert safe_divide(1, 0) is None
    assert safe_divide("1", 2) == "invalid"


def test_more():
    assert safe_divide(0, 5) == 0
    assert safe_divide(5, "x") == "invalid"
    assert safe_divide(None, 1) == "invalid"
    assert safe_divide(1.5, 0.0) is None

from solution import safe_int


def test_examples():
    assert safe_int("42") == 42
    assert safe_int("abc") == 0
    assert safe_int("abc", -1) == -1
    assert safe_int("") == 0


def test_more():
    assert safe_int(" 7 ") == 7
    assert safe_int("-3") == -3
    assert safe_int("3.5", 99) == 99, "a float string is not a valid int"

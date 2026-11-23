from solution import to_paise


def test_examples():
    assert to_paise("19.99") == 1999
    assert to_paise("5") == 500
    assert to_paise("0.10") == 10
    assert to_paise(" 2.5 ") == 250


def test_float_trap():
    # int(float("x") * 100) gets these wrong
    assert to_paise("19.99") == 1999
    assert to_paise("1.15") == 115
    assert to_paise("4.35") == 435
    assert to_paise("0.29") == 29


def test_returns_int():
    assert isinstance(to_paise("1.00"), int)

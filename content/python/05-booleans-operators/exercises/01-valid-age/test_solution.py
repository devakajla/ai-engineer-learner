from solution import is_valid_age


def test_valid():
    assert is_valid_age(25) is True
    assert is_valid_age(0) is True
    assert is_valid_age(120) is True


def test_out_of_range():
    assert is_valid_age(121) is False
    assert is_valid_age(-1) is False


def test_wrong_types_do_not_crash():
    assert is_valid_age("25") is False, "check the type BEFORE comparing (short-circuit)"
    assert is_valid_age(25.0) is False
    assert is_valid_age(None) is False
    assert is_valid_age(True) is False

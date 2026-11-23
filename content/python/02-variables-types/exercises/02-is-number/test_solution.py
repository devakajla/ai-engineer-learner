from solution import is_number


def test_numbers():
    assert is_number(3) is True
    assert is_number(-7) is True
    assert is_number(2.5) is True
    assert is_number(0) is True


def test_not_numbers():
    assert is_number("3") is False
    assert is_number(None) is False
    assert is_number([1]) is False


def test_bools_are_not_numbers():
    assert is_number(True) is False, "bool is a subclass of int — exclude it"
    assert is_number(False) is False

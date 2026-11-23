from solution import has_digit


def test_examples():
    assert has_digit(1234, 3) is True
    assert has_digit(1234, 5) is False
    assert has_digit(0, 0) is True


def test_more():
    assert has_digit(0, 5) is False
    assert has_digit(1000, 0) is True
    assert has_digit(7, 7) is True
    assert has_digit(98765, 4) is False

from solution import reverse_number


def test_examples():
    assert reverse_number(1234) == 4321
    assert reverse_number(1200) == 21, "trailing zeros disappear"
    assert reverse_number(5) == 5


def test_more():
    assert reverse_number(0) == 0
    assert reverse_number(100) == 1
    assert reverse_number(9081) == 1809

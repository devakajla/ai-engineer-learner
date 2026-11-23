from solution import count_digits


def test_examples():
    assert count_digits(1234) == 4
    assert count_digits(7) == 1
    assert count_digits(0) == 1, "zero has one digit"


def test_more():
    assert count_digits(10) == 2
    assert count_digits(1_000_000) == 7

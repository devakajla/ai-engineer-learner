from solution import is_leap


def test_examples():
    assert is_leap(2024) is True
    assert is_leap(1900) is False
    assert is_leap(2000) is True


def test_more():
    assert is_leap(2023) is False
    assert is_leap(2100) is False
    assert is_leap(1996) is True
    assert is_leap(2400) is True

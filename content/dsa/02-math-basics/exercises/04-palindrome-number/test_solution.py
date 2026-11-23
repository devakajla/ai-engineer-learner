from solution import is_palindrome_number


def test_examples():
    assert is_palindrome_number(121) is True
    assert is_palindrome_number(123) is False
    assert is_palindrome_number(10) is False, "10 reversed is 1"


def test_more():
    assert is_palindrome_number(0) is True
    assert is_palindrome_number(7) is True
    assert is_palindrome_number(1221) is True
    assert is_palindrome_number(12321) is True
    assert is_palindrome_number(1231) is False

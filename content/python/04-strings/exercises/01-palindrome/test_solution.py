from solution import is_palindrome


def test_examples():
    assert is_palindrome("racecar") is True
    assert is_palindrome("Never odd or even") is True
    assert is_palindrome("python") is False
    assert is_palindrome("") is True


def test_case_insensitive():
    assert is_palindrome("Abba") is True


def test_near_miss():
    assert is_palindrome("ab") is False
    assert is_palindrome("a") is True

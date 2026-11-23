from solution import is_palindrome


def test_examples():
    assert is_palindrome("Madam") is True
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("hello") is False


def test_more():
    assert is_palindrome("") is True
    assert is_palindrome("a") is True
    assert is_palindrome("ab") is False
    assert is_palindrome("12321") is True
    assert is_palindrome("No 'x' in Nixon") is True

from solution import is_palindrome


def test_examples():
    assert is_palindrome("A man, a plan, a canal: Panama") is True
    assert is_palindrome("race a car") is False


def test_edges():
    assert is_palindrome("") is True
    assert is_palindrome(" ") is True, "no letters: still a palindrome"
    assert is_palindrome("a") is True
    assert is_palindrome("ab") is False
    assert is_palindrome("0P") is False, "digit 0 and letter P are different"
    assert is_palindrome("Aa") is True
    assert is_palindrome(".,!") is True
    assert is_palindrome("ab,,ba") is True
    assert is_palindrome("ab_a") is True, "_ is not a letter or digit, so it is skipped"

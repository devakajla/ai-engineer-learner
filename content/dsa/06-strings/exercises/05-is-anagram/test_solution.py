from solution import is_anagram


def test_examples():
    assert is_anagram("listen", "silent") is True
    assert is_anagram("abc", "abd") is False
    assert is_anagram("Aab", "baa") is True


def test_more():
    assert is_anagram("", "") is True
    assert is_anagram("a", "aa") is False, "different lengths"
    assert is_anagram("rat", "car") is False
    assert is_anagram("aabb", "abab") is True

from solution import is_anagram


def test_examples():
    assert is_anagram("Listen", "Silent") is True
    assert is_anagram("Dormitory", "dirty room") is True
    assert is_anagram("abc", "abd") is False


def test_more():
    assert is_anagram("", "") is True
    assert is_anagram("aab", "abb") is False, "counts must match"
    assert is_anagram("a", "aa") is False
    assert is_anagram("A gentleman", "Elegant man") is True

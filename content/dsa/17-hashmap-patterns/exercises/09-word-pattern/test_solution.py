from solution import word_pattern


def test_examples():
    assert word_pattern("abba", "dog cat cat dog") is True
    assert word_pattern("abba", "dog dog dog dog") is False


def test_more():
    assert word_pattern("abba", "dog cat cat fish") is False
    assert word_pattern("aaaa", "dog cat cat dog") is False
    assert word_pattern("abc", "b c a") is True


def test_lengths():
    assert word_pattern("aaa", "dog dog") is False
    assert word_pattern("a", "dog dog") is False
    assert word_pattern("", "") is True

from solution import top_chars


def test_examples():
    assert top_chars("Hello World", 2) == [("l", 3), ("o", 2)]
    assert top_chars("aabb", 5) == [("a", 2), ("b", 2)]
    assert top_chars("", 3) == []


def test_more():
    assert top_chars("ba", 1) == [("a", 1)], "ties are broken alphabetically"
    assert top_chars("a  b", 5) == [("a", 1), ("b", 1)], "spaces are ignored"
    assert top_chars("AaA", 1) == [("a", 3)]
    assert top_chars("abc", 0) == []

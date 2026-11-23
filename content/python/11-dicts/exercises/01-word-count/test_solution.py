from solution import word_count


def test_examples():
    assert word_count("the cat and The dog") == {"the": 2, "cat": 1, "and": 1, "dog": 1}
    assert word_count("") == {}


def test_more():
    assert word_count("a a a") == {"a": 3}
    assert word_count("  spaced   out  ") == {"spaced": 1, "out": 1}, "split() handles extra spaces"

from solution import top_k_words


def test_examples():
    assert top_k_words("the cat the dog the end cat", 2) == ["the", "cat"]
    assert top_k_words("b a b a c", 2) == ["a", "b"]


def test_more():
    assert top_k_words("", 3) == []
    assert top_k_words("Hi hi HI there", 1) == ["hi"]
    assert top_k_words("x y", 5) == ["x", "y"]
    assert top_k_words("x y", 0) == []

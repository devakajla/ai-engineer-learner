from solution import reverse_words


def test_examples():
    assert reverse_words("the sky is blue") == "blue is sky the"
    assert reverse_words("  hello   world ") == "world hello"


def test_more():
    assert reverse_words("") == ""
    assert reverse_words("one") == "one"
    assert reverse_words("a b c d") == "d c b a"

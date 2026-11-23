from solution import longest_word


def test_examples():
    assert longest_word("I love programming") == "programming"
    assert longest_word("cat dog") == "cat"


def test_more():
    assert longest_word("") == ""
    assert longest_word("   ") == ""
    assert longest_word("a") == "a"

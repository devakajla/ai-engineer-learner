from solution import compress


def test_examples():
    assert compress("aaabbc") == "a3b2c1"
    assert compress("abc") == "a1b1c1"
    assert compress("") == ""


def test_more():
    assert compress("a") == "a1"
    assert compress("aaaaaaaaaaaa") == "a12", "counts can have two digits"
    assert compress("aabaa") == "a2b1a2"

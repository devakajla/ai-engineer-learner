from solution import caesar


def test_examples():
    assert caesar("abc", 1) == "bcd"
    assert caesar("xyz", 3) == "abc"
    assert caesar("Hello, World!", 2) == "Jgnnq, Yqtnf!"


def test_more():
    assert caesar("", 5) == ""
    assert caesar("abc", 0) == "abc"
    assert caesar("abc", -1) == "zab"
    assert caesar("abc", 26) == "abc"
    assert caesar("ABC xyz", 27) == "BCD yza"

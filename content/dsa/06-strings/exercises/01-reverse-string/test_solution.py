from solution import reverse_string


def test_examples():
    assert reverse_string("hello") == "olleh"
    assert reverse_string("") == ""


def test_more():
    assert reverse_string("a") == "a"
    assert reverse_string("ab cd") == "dc ba"

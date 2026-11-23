from solution import greet


def test_examples():
    assert greet("Dev") == "Hello, Dev!"
    assert greet("World") == "Hello, World!"


def test_returns_not_prints():
    assert greet("A") is not None, "greet must RETURN the string, not print it"


def test_empty_name():
    assert greet("") == "Hello, !"

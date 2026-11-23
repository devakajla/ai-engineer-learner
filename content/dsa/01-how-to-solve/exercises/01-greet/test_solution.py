from solution import greet


def test_examples():
    assert greet("Dev") == "Hello, Dev!", "greet('Dev') should be 'Hello, Dev!'"
    assert greet("Asha") == "Hello, Asha!"


def test_edge():
    assert greet("") == "Hello, !", "empty name still works"
    assert isinstance(greet("x"), str), "return a string, do not print it"

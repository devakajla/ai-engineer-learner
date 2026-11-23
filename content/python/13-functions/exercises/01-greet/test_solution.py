from solution import greet


def test_examples():
    assert greet("Dev") == "Hello, Dev!"
    assert greet("Dev", "Namaste") == "Namaste, Dev!"


def test_keyword():
    assert greet(name="Ada", greeting="Hi") == "Hi, Ada!"
    assert greet("") == "Hello, !"

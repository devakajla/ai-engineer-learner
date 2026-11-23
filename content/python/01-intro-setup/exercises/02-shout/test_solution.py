from solution import shout


def test_examples():
    assert shout("hello") == "HELLO!!!"
    assert shout("Python 3") == "PYTHON 3!!!"


def test_already_upper():
    assert shout("OK") == "OK!!!"


def test_empty():
    assert shout("") == "!!!"

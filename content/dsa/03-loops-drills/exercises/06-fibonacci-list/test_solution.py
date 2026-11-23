from solution import fibonacci


def test_examples():
    assert fibonacci(6) == [0, 1, 1, 2, 3, 5]
    assert fibonacci(1) == [0]
    assert fibonacci(0) == []


def test_more():
    assert fibonacci(2) == [0, 1]
    assert fibonacci(10) == [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

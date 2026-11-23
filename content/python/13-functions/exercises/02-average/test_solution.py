from solution import average


def test_examples():
    assert average(2, 4, 6) == 4.0
    assert average(10) == 10.0
    assert average() == 0


def test_more():
    assert average(1, 2) == 1.5
    assert average(-1, 1) == 0
    assert average(*[1, 2, 3, 4]) == 2.5

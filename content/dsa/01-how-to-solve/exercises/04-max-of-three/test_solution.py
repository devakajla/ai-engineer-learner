from solution import biggest


def test_examples():
    assert biggest(1, 5, 3) == 5
    assert biggest(9, 2, 9) == 9


def test_more():
    assert biggest(-1, -5, -3) == -1, "all negative"
    assert biggest(7, 7, 7) == 7, "all equal"
    assert biggest(3, 2, 1) == 3, "first is biggest"
    assert biggest(1, 2, 3) == 3, "last is biggest"

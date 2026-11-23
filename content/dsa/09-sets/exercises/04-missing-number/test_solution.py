from solution import missing_number


def test_examples():
    assert missing_number([3, 0, 1]) == 2
    assert missing_number([0, 1]) == 2
    assert missing_number([1]) == 0


def test_more():
    assert missing_number([0]) == 1
    assert missing_number([9, 6, 4, 2, 3, 5, 7, 0, 1]) == 8
    assert missing_number(list(range(1, 101))) == 0

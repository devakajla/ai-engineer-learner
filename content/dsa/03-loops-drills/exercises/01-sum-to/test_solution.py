from solution import sum_to


def test_examples():
    assert sum_to(5) == 15
    assert sum_to(1) == 1
    assert sum_to(0) == 0


def test_more():
    assert sum_to(100) == 5050

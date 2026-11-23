from solution import digit_sum


def test_examples():
    assert digit_sum(1234) == 10
    assert digit_sum(9) == 9
    assert digit_sum(0) == 0


def test_more():
    assert digit_sum(1000) == 1, "zeros add nothing"
    assert digit_sum(99999) == 45

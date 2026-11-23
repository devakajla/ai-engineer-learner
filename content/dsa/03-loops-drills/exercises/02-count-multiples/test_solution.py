from solution import count_multiples


def test_examples():
    assert count_multiples(10, 3) == 3
    assert count_multiples(5, 7) == 0


def test_more():
    assert count_multiples(10, 1) == 10
    assert count_multiples(10, 5) == 2, "n itself counts"
    assert count_multiples(0, 3) == 0

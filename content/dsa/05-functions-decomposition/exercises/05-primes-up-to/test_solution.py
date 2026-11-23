from solution import primes_up_to


def test_examples():
    assert primes_up_to(10) == [2, 3, 5, 7]
    assert primes_up_to(1) == []
    assert primes_up_to(2) == [2]


def test_more():
    assert primes_up_to(0) == []
    assert primes_up_to(30) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    assert len(primes_up_to(100)) == 25

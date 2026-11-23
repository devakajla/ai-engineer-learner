from solution import is_prime


def test_examples():
    assert is_prime(7) is True
    assert is_prime(12) is False
    assert is_prime(1) is False


def test_edges():
    assert is_prime(0) is False
    assert is_prime(2) is True, "2 is the smallest prime"
    assert is_prime(3) is True
    assert is_prime(4) is False, "4 = 2 * 2"
    assert is_prime(9) is False, "perfect square of a prime"
    assert is_prime(97) is True
    assert is_prime(7919) is True
    assert is_prime(7917) is False

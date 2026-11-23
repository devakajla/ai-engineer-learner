from solution import gcd


def test_examples():
    assert gcd(12, 18) == 6
    assert gcd(7, 13) == 1
    assert gcd(10, 10) == 10


def test_more():
    assert gcd(1, 99) == 1
    assert gcd(100, 75) == 25
    assert gcd(48, 18) == 6
    assert gcd(17, 34) == 17, "one divides the other"

from solution import fast_power


def test_examples():
    assert fast_power(2, 10) == 1024
    assert fast_power(5, 0) == 1


def test_many():
    for x in range(-3, 4):
        for n in range(0, 20):
            assert fast_power(x, n) == x ** n, f"{x}^{n}"


def test_huge_exponent_must_be_fast():
    assert fast_power(1, 10 ** 6) == 1, "linear recursion is too deep: halve n"
    assert fast_power(-1, 10 ** 6 + 1) == -1

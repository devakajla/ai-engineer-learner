from solution import factorial


def test_examples():
    assert factorial(5) == 120
    assert factorial(1) == 1
    assert factorial(0) == 1


def test_more():
    assert factorial(3) == 6
    assert factorial(10) == 3628800
    assert factorial(20) == 2432902008176640000

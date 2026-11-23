from solution import fib


def test_examples():
    assert fib(10) == 55
    assert fib(40) == 102334155, "too slow? remember answers in a dict"


def test_edges():
    assert fib(0) == 0
    assert fib(1) == 1
    assert fib(2) == 1


def test_many():
    a, b = 0, 1
    for n in range(0, 60):
        assert fib(n) == a, f"n = {n}"
        a, b = b, a + b

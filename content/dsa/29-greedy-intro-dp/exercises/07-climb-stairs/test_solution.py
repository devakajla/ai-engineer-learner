from solution import climb_stairs


def brute(n):
    if n <= 1:
        return 1
    return brute(n - 1) + brute(n - 2)


def test_examples():
    assert climb_stairs(3) == 3
    assert climb_stairs(1) == 1


def test_small():
    for n in range(1, 15):
        assert climb_stairs(n) == brute(n), f"n={n}"


def test_big():
    assert climb_stairs(45) == 1836311903, "must be fast: no plain recursion"

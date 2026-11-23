import random
from solution import sum_list


def test_examples():
    assert sum_list([1, 2, 3, 4]) == 10
    assert sum_list([]) == 0


def test_random():
    rng = random.Random(1)
    for _ in range(100):
        v = [rng.randint(-9, 9) for _ in range(rng.randint(0, 20))]
        assert sum_list(v) == sum(v), f"{v}"

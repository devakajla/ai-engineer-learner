import random
from solution import max_of_list


def test_examples():
    assert max_of_list([3, 9, 2]) == 9
    assert max_of_list([5]) == 5


def test_random():
    rng = random.Random(2)
    for _ in range(100):
        v = [rng.randint(-50, 50) for _ in range(rng.randint(1, 20))]
        assert max_of_list(v) == max(v), f"{v}"

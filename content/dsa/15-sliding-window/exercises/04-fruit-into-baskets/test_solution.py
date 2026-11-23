import random
from solution import total_fruit


def brute(fruits):
    best = 0
    for i in range(len(fruits)):
        for j in range(i, len(fruits)):
            if len(set(fruits[i:j + 1])) <= 2:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert total_fruit([1, 2, 3, 2, 2]) == 4
    assert total_fruit([1, 2, 1]) == 3


def test_edges():
    assert total_fruit([]) == 0
    assert total_fruit([7]) == 1
    assert total_fruit([0, 1, 2, 2]) == 3
    assert total_fruit([3, 3, 3, 1, 2, 1, 1, 2, 3, 3, 4]) == 5


def test_random():
    rng = random.Random(4)
    for _ in range(300):
        fruits = [rng.randint(0, 3) for _ in range(rng.randint(0, 12))]
        assert total_fruit(fruits) == brute(fruits), f"{fruits}"

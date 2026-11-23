import random
from collections import Counter
from solution import least_interval


def formula(tasks, n):
    if not tasks:
        return 0
    c = Counter(tasks)
    top = max(c.values())
    return max(len(tasks), (top - 1) * (n + 1) + sum(1 for v in c.values() if v == top))


def test_examples():
    assert least_interval(["A", "A", "A", "B", "B", "B"], 2) == 8
    assert least_interval(["A", "A", "B"], 0) == 3


def test_edges():
    assert least_interval([], 3) == 0
    assert least_interval(["A"], 5) == 1
    assert least_interval(["A", "A", "A"], 3) == 9


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        tasks = [rng.choice("ABCD") for _ in range(rng.randint(0, 12))]
        n = rng.randint(0, 4)
        assert least_interval(list(tasks), n) == formula(tasks, n), f"{tasks}, {n}"

import random
from solution import heap_sort


def test_examples():
    assert heap_sort([5, 1, 4, 2]) == [1, 2, 4, 5]
    assert heap_sort([]) == []


def test_random():
    rng = random.Random(1)
    for _ in range(100):
        v = [rng.randint(-9, 9) for _ in range(rng.randint(0, 12))]
        copy = list(v)
        assert heap_sort(v) == sorted(v), f"{v}"
        assert v == copy, "do not change the input"

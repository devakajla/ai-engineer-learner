import random
from solution import remove_covered


def brute(iv):
    return sum(1 for i, (a, b) in enumerate(iv) if not any(j != i and c <= a and b <= d for j, (c, d) in enumerate(iv)))


def test_examples():
    assert remove_covered([[1, 4], [3, 6], [2, 8]]) == 2
    assert remove_covered([[1, 4], [2, 3]]) == 1


def test_edges():
    assert remove_covered([]) == 0
    assert remove_covered([[1, 2]]) == 1
    assert remove_covered([[1, 5], [1, 3]]) == 1, "same start: the longer one covers the shorter"
    assert remove_covered([[1, 2], [3, 4]]) == 2


def test_random():
    rng = random.Random(10)
    for _ in range(300):
        seen, iv = set(), []
        for _ in range(rng.randint(0, 6)):
            s = rng.randint(0, 8)
            pair = (s, s + rng.randint(1, 5))
            if pair not in seen:
                seen.add(pair)
                iv.append(list(pair))
        assert remove_covered(iv) == brute(iv), f"{iv}"

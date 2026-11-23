import random
from solution import first_unique_index


def brute(s):
    for i, ch in enumerate(s):
        if s.count(ch) == 1:
            return i
    return -1


def test_examples():
    assert first_unique_index("loveleetcode") == 2
    assert first_unique_index("aabb") == -1


def test_edges():
    assert first_unique_index("") == -1
    assert first_unique_index("z") == 0
    assert first_unique_index("aabbc") == 4


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 10)))
        assert first_unique_index(s) == brute(s), f"{s!r}"

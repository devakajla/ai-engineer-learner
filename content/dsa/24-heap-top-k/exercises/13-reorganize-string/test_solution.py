import random
from collections import Counter
from itertools import permutations
from solution import reorganize


def possible(s):
    return any(all(a != b for a, b in zip(p, p[1:])) for p in set(permutations(s)))


def test_examples():
    assert reorganize("aab") == "aba"
    assert reorganize("aaab") == ""


def test_edges():
    assert reorganize("") == ""
    assert reorganize("a") == "a"


def test_random():
    rng = random.Random(13)
    for _ in range(150):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        got = reorganize(s)
        if s == "" or possible(s):
            assert Counter(got) == Counter(s), f"{s!r}: letters changed, got {got!r}"
            assert all(a != b for a, b in zip(got, got[1:])), f"{s!r}: neighbours equal in {got!r}"
        else:
            assert got == "", f"{s!r} is impossible, got {got!r}"

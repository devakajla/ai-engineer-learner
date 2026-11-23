import random
from solution import lcs_length


def brute(a, b):
    best = 0
    n = len(a)
    for mask in range(1 << n):
        sub = [a[i] for i in range(n) if mask >> i & 1]
        j = 0
        for ch in b:
            if j < len(sub) and sub[j] == ch:
                j += 1
        if j == len(sub):
            best = max(best, len(sub))
    return best


def test_examples():
    assert lcs_length("abcde", "ace") == 3
    assert lcs_length("abc", "def") == 0


def test_edges():
    assert lcs_length("", "abc") == 0
    assert lcs_length("same", "same") == 4


def test_random():
    rng = random.Random(16)
    for _ in range(300):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 7)))
        assert lcs_length(a, b) == brute(a, b), f"{a!r}, {b!r}"

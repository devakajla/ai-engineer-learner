import random
from solution import longest_two_kinds


def brute(s):
    best = 0
    for i in range(len(s)):
        for j in range(i, len(s)):
            if len(set(s[i:j + 1])) <= 2:
                best = max(best, j - i + 1)
    return best


def test_examples():
    assert longest_two_kinds("eceba") == 3
    assert longest_two_kinds("ccaabbb") == 5


def test_edges():
    assert longest_two_kinds("") == 0
    assert longest_two_kinds("a") == 1
    assert longest_two_kinds("abc") == 2


def test_random():
    rng = random.Random(2)
    for _ in range(300):
        s = "".join(rng.choice("abcd") for _ in range(rng.randint(0, 12)))
        assert longest_two_kinds(s) == brute(s), f"{s!r}"

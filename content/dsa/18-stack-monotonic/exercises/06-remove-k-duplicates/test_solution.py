import random
from solution import remove_k_duplicates


def brute(s, k):
    changed = True
    while changed:
        changed = False
        for i in range(len(s) - k + 1):
            if s[i:i + k] == s[i] * k:
                s = s[:i] + s[i + k:]
                changed = True
                break
    return s


def test_examples():
    assert remove_k_duplicates("deeedbbcccbdaa", 3) == "aa"
    assert remove_k_duplicates("abcd", 2) == "abcd"


def test_edges():
    assert remove_k_duplicates("", 3) == ""
    assert remove_k_duplicates("pbbcggttciiippooaais", 2) == "ps"
    assert remove_k_duplicates("aaaa", 3) == "a"


def test_random():
    rng = random.Random(6)
    for _ in range(300):
        s = "".join(rng.choice("ab") for _ in range(rng.randint(0, 12)))
        k = rng.randint(2, 4)
        assert remove_k_duplicates(s, k) == brute(s, k), f"{s!r}, {k}"

import random
from solution import remove_adjacent_duplicates


def brute(s):
    changed = True
    while changed:
        changed = False
        for i in range(len(s) - 1):
            if s[i] == s[i + 1]:
                s = s[:i] + s[i + 2:]
                changed = True
                break
    return s


def test_examples():
    assert remove_adjacent_duplicates("abbaca") == "ca"
    assert remove_adjacent_duplicates("azxxzy") == "ay"


def test_edges():
    assert remove_adjacent_duplicates("") == ""
    assert remove_adjacent_duplicates("aa") == ""
    assert remove_adjacent_duplicates("abc") == "abc"
    assert remove_adjacent_duplicates("abba") == ""


def test_random():
    rng = random.Random(1)
    for _ in range(300):
        s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 12)))
        assert remove_adjacent_duplicates(s) == brute(s), f"{s!r}"

import random
from solution import longest_valid_parentheses


def valid(s):
    bal = 0
    for ch in s:
        bal += 1 if ch == "(" else -1
        if bal < 0:
            return False
    return bal == 0


def brute(s):
    best = 0
    for i in range(len(s)):
        for j in range(i + 2, len(s) + 1, 2):
            if valid(s[i:j]):
                best = max(best, j - i)
    return best


def test_examples():
    assert longest_valid_parentheses(")()())") == 4
    assert longest_valid_parentheses("(()") == 2


def test_edges():
    assert longest_valid_parentheses("") == 0
    assert longest_valid_parentheses("()(()") == 2
    assert longest_valid_parentheses("()(())") == 6
    assert longest_valid_parentheses("))))") == 0


def test_random():
    rng = random.Random(8)
    for _ in range(400):
        s = "".join(rng.choice("()") for _ in range(rng.randint(0, 12)))
        assert longest_valid_parentheses(s) == brute(s), f"{s!r}"

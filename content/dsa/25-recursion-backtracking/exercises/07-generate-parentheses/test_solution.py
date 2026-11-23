from itertools import product
from solution import generate_parentheses


def valid(s):
    depth = 0
    for ch in s:
        depth += 1 if ch == "(" else -1
        if depth < 0:
            return False
    return depth == 0


def brute(n):
    return sorted("".join(p) for p in product("()", repeat=2 * n) if valid("".join(p)))


def test_examples():
    assert generate_parentheses(1) == ["()"]
    assert sorted(generate_parentheses(2)) == ["(())", "()()"]


def test_edges():
    assert generate_parentheses(0) == [""]


def test_many():
    for n in range(0, 7):
        got = generate_parentheses(n)
        assert len(got) == len(set(got)), f"n={n}: duplicates"
        assert sorted(got) == brute(n), f"n={n}"

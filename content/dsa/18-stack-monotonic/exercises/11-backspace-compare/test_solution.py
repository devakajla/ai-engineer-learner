import random
from solution import backspace_compare


def typed(text):
    out = ""
    for ch in text:
        out = out[:-1] if ch == "#" else out + ch
    return out


def test_examples():
    assert backspace_compare("ab#c", "ad#c") is True
    assert backspace_compare("a#c", "b") is False


def test_edges():
    assert backspace_compare("a##c", "#a#c") is True
    assert backspace_compare("", "#") is True
    assert backspace_compare("ab##", "c#d#") is True


def test_random():
    rng = random.Random(11)
    for _ in range(300):
        s = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 8)))
        t = "".join(rng.choice("ab#") for _ in range(rng.randint(0, 8)))
        assert backspace_compare(s, t) is (typed(s) == typed(t)), f"{s!r}, {t!r}"

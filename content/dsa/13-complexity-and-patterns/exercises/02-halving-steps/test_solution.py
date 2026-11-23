from solution import halving_steps


def test_examples():
    assert halving_steps(8) == 3
    assert halving_steps(10) == 3


def test_edges():
    assert halving_steps(1) == 0, "already 1: zero steps"
    assert halving_steps(2) == 1
    assert halving_steps(3) == 1
    assert halving_steps(1000) == 9
    assert halving_steps(10**6) == 19
    assert halving_steps(2**40) == 40

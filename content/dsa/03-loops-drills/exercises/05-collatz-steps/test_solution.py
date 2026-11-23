from solution import collatz_steps


def test_examples():
    assert collatz_steps(6) == 8
    assert collatz_steps(1) == 0


def test_more():
    assert collatz_steps(2) == 1
    assert collatz_steps(3) == 7
    assert collatz_steps(27) == 111

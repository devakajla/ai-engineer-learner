from solution import fits


def test_examples():
    assert fits(1000, 500, 4096) is True
    assert fits(4000, 500, 4096) is False
    assert fits(3596, 500, 4096) is True


def test_edges():
    assert fits(3597, 500, 4096) is False, "one token over the limit does not fit"
    assert fits(0, 0, 10) is True
    assert fits(10, 0, 10) is True
    assert fits(0, 11, 10) is False

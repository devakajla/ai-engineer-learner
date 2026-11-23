from solution import rectangle


def test_examples():
    assert rectangle(3, 4) == (12, 14)
    assert rectangle(5, 5) == (25, 20)


def test_edges():
    assert rectangle(0, 7) == (0, 14), "zero width"
    assert rectangle(1, 1) == (1, 4)
    assert rectangle(2.5, 2) == (5.0, 9.0)

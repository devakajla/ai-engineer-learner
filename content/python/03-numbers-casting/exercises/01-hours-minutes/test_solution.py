from solution import to_hours_minutes


def test_examples():
    assert tuple(to_hours_minutes(135)) == (2, 15)
    assert tuple(to_hours_minutes(59)) == (0, 59)
    assert tuple(to_hours_minutes(0)) == (0, 0)


def test_exact_hours():
    assert tuple(to_hours_minutes(120)) == (2, 0)


def test_returns_ints():
    h, m = to_hours_minutes(61)
    assert isinstance(h, int) and isinstance(m, int), "use // or divmod, not /"

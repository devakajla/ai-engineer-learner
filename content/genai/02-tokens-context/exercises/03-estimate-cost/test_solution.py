from solution import estimate_cost


def test_examples():
    assert estimate_cost(1_000_000, 1_000_000, 0.5, 1.5) == 2.0
    assert estimate_cost(1000, 500, 0.05, 0.08) == 0.00009
    assert estimate_cost(0, 0, 0.5, 1.5) == 0.0


def test_edges():
    assert estimate_cost(2_000_000, 0, 0.5, 9) == 1.0, "no output tokens means no output cost"
    assert estimate_cost(0, 500_000, 9, 2) == 1.0, "no input tokens means no input cost"
    assert estimate_cost(123, 456, 1, 1) == 0.000579, "round to 6 decimal places"

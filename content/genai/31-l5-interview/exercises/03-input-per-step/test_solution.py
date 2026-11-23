from solution import agent_input_cost, input_per_step


def test_per_step():
    assert input_per_step(100, [50, 50, 50]) == [100, 150, 200]


def test_uneven_additions():
    assert input_per_step(10, [5, 100, 1]) == [10, 15, 115]


def test_empty():
    assert input_per_step(100, []) == []
    assert agent_input_cost(100, [], 1.0) == 0.0


def test_cost():
    assert agent_input_cost(100, [50, 50, 50], 1.0) == 0.00045


def test_growth_is_more_than_linear():
    ten = sum(input_per_step(100, [500] * 10))
    assert ten == 100 * 10 + 500 * (0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9)
    assert ten > 10 * 100 + 10 * 500


def test_price_scaling():
    assert agent_input_cost(1_000_000, [0], 2.0) == 2.0

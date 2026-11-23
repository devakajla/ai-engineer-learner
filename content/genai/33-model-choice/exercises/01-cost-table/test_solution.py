from solution import cost_table

MODELS = {
    "small": {"input_price": 0.05, "output_price": 0.08},
    "big": {"input_price": 0.6, "output_price": 0.8},
}


def test_example():
    assert cost_table(MODELS, 1000, 500) == {"small": 9e-05, "big": 0.001}


def test_empty_and_order():
    assert cost_table({}, 10, 10) == {}
    assert list(cost_table(MODELS, 1, 1)) == ["small", "big"], "keep the order of the models"


def test_zero_tokens():
    assert cost_table(MODELS, 0, 0) == {"small": 0.0, "big": 0.0}


def test_output_price_is_used():
    result = cost_table({"m": {"input_price": 0, "output_price": 2}}, 1_000_000, 1_000_000)
    assert result == {"m": 2.0}, "input costs 0 here, so the whole cost is the output cost"

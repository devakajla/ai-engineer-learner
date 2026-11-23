from solution import cheapest_that_fits

MODELS = {
    "small": {"input_price": 0.05, "output_price": 0.08, "context": 8000},
    "big": {"input_price": 0.6, "output_price": 0.8, "context": 128000},
}


def test_examples():
    assert cheapest_that_fits(MODELS, 1000, 500) == "small"
    assert cheapest_that_fits(MODELS, 20000, 500) == "big"
    assert cheapest_that_fits(MODELS, 999999, 500) is None


def test_exact_fit():
    assert cheapest_that_fits(MODELS, 7500, 500) == "small", "using the whole window is allowed"
    assert cheapest_that_fits(MODELS, 7501, 500) == "big"


def test_cheapest_is_not_always_first():
    models = {
        "pricey": {"input_price": 5, "output_price": 5, "context": 1000},
        "cheap": {"input_price": 1, "output_price": 1, "context": 1000},
    }
    assert cheapest_that_fits(models, 10, 10) == "cheap"


def test_tie_returns_first_and_empty():
    models = {
        "a": {"input_price": 1, "output_price": 1, "context": 1000},
        "b": {"input_price": 1, "output_price": 1, "context": 1000},
    }
    assert cheapest_that_fits(models, 10, 10) == "a"
    assert cheapest_that_fits({}, 10, 10) is None

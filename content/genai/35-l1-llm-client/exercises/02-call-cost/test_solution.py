from types import SimpleNamespace as NS

from solution import call_cost


def make_response(prompt, completion, finish="stop"):
    return NS(
        choices=[NS(message=NS(content="x"), finish_reason=finish)],
        usage=NS(prompt_tokens=prompt, completion_tokens=completion, total_tokens=prompt + completion),
    )


def test_example():
    result = call_cost(make_response(1000, 500), 0.5, 1.5)
    assert result == {
        "usage": {"input": 1000, "output": 500, "total": 1500},
        "cost": 0.00125,
        "cut_off": False,
    }


def test_cut_off_flag():
    assert call_cost(make_response(10, 10, "length"), 1, 1)["cut_off"] is True
    assert call_cost(make_response(10, 10, "stop"), 1, 1)["cut_off"] is False


def test_zero_tokens():
    result = call_cost(make_response(0, 0), 0.5, 1.5)
    assert result["cost"] == 0.0
    assert result["usage"]["total"] == 0


def test_prices_are_used():
    result = call_cost(make_response(1_000_000, 1_000_000), 2.0, 3.0)
    assert result["cost"] == 5.0, "input costs 2.0 and output costs 3.0 per million"

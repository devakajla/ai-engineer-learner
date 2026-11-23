import pytest

from solution import monthly_cost, request_cost


def test_request_cost_uses_prices_per_million_tokens():
    assert request_cost(1000, 500, 0.5, 1.5) == pytest.approx(0.00125)
    assert request_cost(1_000_000, 0, 0.5, 1.5) == pytest.approx(0.5)
    assert request_cost(0, 1_000_000, 0.5, 1.5) == pytest.approx(1.5)
    assert request_cost(0, 0, 0.5, 1.5) == 0


def test_monthly_cost():
    assert monthly_cost(1000, 2000, 500, 0.5, 1.5) == 52.5
    assert monthly_cost(1000, 2000, 500, 0.5, 1.5, days=31) == 54.25


def test_rounds_to_two_decimals():
    assert monthly_cost(7, 333, 111, 0.59, 0.79) == 0.06


def test_zero_traffic_costs_nothing():
    assert monthly_cost(0, 2000, 500, 0.5, 1.5) == 0

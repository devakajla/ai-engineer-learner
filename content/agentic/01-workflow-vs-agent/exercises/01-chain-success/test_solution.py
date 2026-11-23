import pytest

from solution import chain_success


def test_examples():
    assert chain_success(0.95, 10) == 0.5987
    assert chain_success(0.99, 5) == 0.951
    assert chain_success(0.8, 3) == 0.512


def test_one_step_is_the_step_chance():
    assert chain_success(0.7, 1) == 0.7


def test_no_steps_cannot_fail():
    assert chain_success(0.5, 0) == 1.0
    assert chain_success(0.5, -3) == 1.0


def test_perfect_and_useless_steps():
    assert chain_success(1.0, 50) == 1.0
    assert chain_success(0.0, 3) == 0.0


def test_more_steps_means_lower_chance():
    assert chain_success(0.9, 12) < chain_success(0.9, 3)


def test_bad_probability():
    with pytest.raises(ValueError):
        chain_success(1.5, 3)
    with pytest.raises(ValueError):
        chain_success(-0.1, 3)

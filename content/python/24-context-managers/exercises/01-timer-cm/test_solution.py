import time

import pytest

from solution import Timer, timer


def test_timer_class():
    with Timer() as t:
        time.sleep(0.01)
    assert t.elapsed >= 0.01


def test_timer_class_exception():
    t = Timer()
    with pytest.raises(ValueError):
        with t:
            time.sleep(0.005)
            raise ValueError
    assert t.elapsed >= 0.005


def test_timer_function():
    results = []
    with timer(results, "q"):
        time.sleep(0.005)
    assert results[0][0] == "q" and results[0][1] >= 0.005


def test_timer_function_exception():
    results = []
    with pytest.raises(KeyError):
        with timer(results, "boom"):
            raise KeyError
    assert [r[0] for r in results] == ["boom"], "use try/finally around the yield"

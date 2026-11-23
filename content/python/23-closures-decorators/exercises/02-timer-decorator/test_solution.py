import time

import pytest

import solution
from solution import timed


def setup_function():
    solution.TIMINGS.clear()


def test_returns_and_records():
    @timed
    def add(a, b):
        """Add two numbers."""
        return a + b

    assert add(2, b=3) == 5
    name, secs = solution.TIMINGS[-1]
    assert name == "add" and secs >= 0


def test_wraps():
    @timed
    def documented():
        """Docs here."""

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Docs here."
    assert documented.__wrapped__ is not None


def test_records_on_exception():
    @timed
    def boom():
        time.sleep(0.01)
        raise RuntimeError("x")

    with pytest.raises(RuntimeError):
        boom()
    assert solution.TIMINGS and solution.TIMINGS[-1][0] == "boom"
    assert solution.TIMINGS[-1][1] >= 0.01

import pytest

from solution import retry


def flaky_factory(failures, exc=ConnectionError):
    state = {"n": 0}

    def fn(x=1):
        """Flaky."""
        state["n"] += 1
        if state["n"] <= failures:
            raise exc("fail")
        return x * 10

    return fn


def test_retries_then_succeeds():
    delays = []
    fn = retry(attempts=3, exceptions=(ConnectionError,), sleep=delays.append)(flaky_factory(2))
    assert fn(4) == 40
    assert delays == [0.5, 1.0]
    assert fn.attempts_made == 3


def test_gives_up():
    fn = retry(attempts=2, exceptions=(ConnectionError,), sleep=lambda s: None)(flaky_factory(5))
    with pytest.raises(ConnectionError):
        fn()
    assert fn.attempts_made == 2


def test_other_errors_not_retried():
    delays = []
    fn = retry(attempts=5, exceptions=(ConnectionError,), sleep=delays.append)(flaky_factory(1, ValueError))
    with pytest.raises(ValueError):
        fn()
    assert delays == [] and fn.attempts_made == 1


def test_wraps_and_decorator_syntax():
    @retry(attempts=2, sleep=lambda s: None)
    def named():
        """Doc."""
        return "ok"

    assert named() == "ok" and named.__name__ == "named" and named.__doc__ == "Doc."
    assert named.attempts_made == 1

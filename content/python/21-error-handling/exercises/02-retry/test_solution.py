import pytest

from solution import retry


def make(seq):
    it = iter(seq)

    def fn():
        item = next(it)
        if isinstance(item, Exception):
            raise item
        return item

    return fn


def test_succeeds_after_retries():
    delays = []
    assert retry(make([ConnectionError(), ConnectionError(), "ok"]), sleep=delays.append) == "ok"
    assert delays == [0.5, 1.0]


def test_gives_up_and_reraises_last():
    delays = []
    last = TimeoutError("third")
    with pytest.raises(TimeoutError, match="third"):
        retry(make([TimeoutError("1"), TimeoutError("2"), last]), sleep=delays.append)
    assert delays == [0.5, 1.0], "no sleep after the final attempt"


def test_no_retry_on_other_errors():
    delays = []
    with pytest.raises(ValueError):
        retry(make([ValueError("bug"), "never"]), sleep=delays.append)
    assert delays == []


def test_custom_settings():
    delays = []
    fn = make([KeyError(), KeyError(), KeyError(), "ok"])
    assert retry(fn, attempts=4, base_delay=1, retry_on=(KeyError,), sleep=delays.append) == "ok"
    assert delays == [1, 2, 4]


def test_first_try_success_no_sleep():
    delays = []
    assert retry(lambda: 42, sleep=delays.append) == 42 and delays == []

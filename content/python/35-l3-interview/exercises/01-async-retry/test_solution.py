import asyncio

import pytest

from solution import retry_async


def make_sleep():
    waits = []

    async def fake_sleep(seconds):
        waits.append(seconds)

    return waits, fake_sleep


def flaky_factory(failures, error=ConnectionError):
    calls = []

    async def flaky():
        calls.append(1)
        if len(calls) <= failures:
            raise error("down")
        return "ok"

    return calls, flaky


def test_success_first_time_no_wait():
    waits, sleep = make_sleep()
    calls, fn = flaky_factory(0)
    assert asyncio.run(retry_async(fn, sleep=sleep)) == "ok"
    assert len(calls) == 1 and waits == []


def test_retries_then_succeeds_with_backoff():
    waits, sleep = make_sleep()
    calls, fn = flaky_factory(2)
    out = asyncio.run(retry_async(fn, attempts=3, base_delay=0.5, retry_on=(ConnectionError,), sleep=sleep))
    assert out == "ok"
    assert len(calls) == 3
    assert waits == [0.5, 1.0]


def test_gives_up_and_raises_last_error_without_final_wait():
    waits, sleep = make_sleep()
    calls, fn = flaky_factory(10)
    with pytest.raises(ConnectionError):
        asyncio.run(retry_async(fn, attempts=3, base_delay=1, retry_on=(ConnectionError,), sleep=sleep))
    assert len(calls) == 3
    assert waits == [1, 2], "wait between attempts only, not after the last one"


def test_other_errors_are_not_retried():
    waits, sleep = make_sleep()
    calls, fn = flaky_factory(5, error=KeyError)
    with pytest.raises(KeyError):
        asyncio.run(retry_async(fn, attempts=3, retry_on=(ConnectionError,), sleep=sleep))
    assert len(calls) == 1 and waits == []


def test_single_attempt():
    waits, sleep = make_sleep()
    calls, fn = flaky_factory(1)
    with pytest.raises(ConnectionError):
        asyncio.run(retry_async(fn, attempts=1, sleep=sleep))
    assert waits == []


def test_bad_attempts():
    with pytest.raises(ValueError):
        asyncio.run(retry_async(lambda: None, attempts=0))

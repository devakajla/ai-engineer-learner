import asyncio
import inspect

import pytest

from solution import call_with_timeout, collect, stream_words


async def never():
    await asyncio.Event().wait()


async def quick():
    await asyncio.sleep(0)
    return "done"


def test_returns_result_when_fast():
    assert asyncio.run(call_with_timeout(quick, 1)) == "done"


def test_returns_default_on_timeout():
    assert asyncio.run(call_with_timeout(never, 0.01, default="late")) == "late"


def test_default_is_none():
    assert asyncio.run(call_with_timeout(never, 0.01)) is None


def test_other_errors_are_not_hidden():
    async def broken():
        raise KeyError("oops")

    with pytest.raises(KeyError):
        asyncio.run(call_with_timeout(broken, 1))


def test_stream_words_is_an_async_generator():
    assert inspect.isasyncgen(stream_words("a b")), "stream_words must be an async generator (async def + yield)"


def test_collect_stream():
    assert asyncio.run(collect(stream_words("a b c"))) == ["a", "b", "c"]


def test_collect_empty():
    assert asyncio.run(collect(stream_words(""))) == []


def test_collect_any_async_generator():
    async def numbers():
        for n in (1, 2, 3):
            yield n

    assert asyncio.run(collect(numbers())) == [1, 2, 3]

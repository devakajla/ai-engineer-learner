import asyncio

import pytest

from solution import limited_gather


def test_results_in_order():
    async def work(x):
        await asyncio.sleep(0)
        return x * 2

    assert asyncio.run(limited_gather(work, [1, 2, 3, 4, 5], limit=2)) == [2, 4, 6, 8, 10]


def test_empty():
    async def work(x):
        return x

    assert asyncio.run(limited_gather(work, [], limit=3)) == []


def test_never_more_than_limit_and_reaches_limit():
    state = {"now": 0, "max": 0}

    async def work(x):
        state["now"] += 1
        state["max"] = max(state["max"], state["now"])
        for _ in range(5):
            await asyncio.sleep(0)
        state["now"] -= 1
        return x

    out = asyncio.run(limited_gather(work, list(range(20)), limit=3))
    assert out == list(range(20))
    assert state["max"] <= 3, f"{state['max']} tasks ran at once, the limit is 3"
    assert state["max"] == 3, "the limit should be used fully, not run one by one"


def test_limit_one_runs_one_by_one():
    state = {"now": 0, "max": 0}

    async def work(x):
        state["now"] += 1
        state["max"] = max(state["max"], state["now"])
        await asyncio.sleep(0)
        state["now"] -= 1
        return x

    asyncio.run(limited_gather(work, [1, 2, 3], limit=1))
    assert state["max"] == 1


def test_bad_limit():
    async def work(x):
        return x

    with pytest.raises(ValueError):
        asyncio.run(limited_gather(work, [1], limit=0))

import asyncio

from solution import fetch_all, fetch_all_safe


async def fake(url):
    await asyncio.sleep(0)
    if url == "bad":
        raise ValueError("bad url")
    return url.upper()


def test_fetch_all_order():
    assert asyncio.run(fetch_all(fake, ["a", "b", "c"])) == ["A", "B", "C"]


def test_fetch_all_empty():
    assert asyncio.run(fetch_all(fake, [])) == []


def test_fetch_all_runs_together():
    async def job(url):
        await barrier.wait()      # only passes if 3 jobs wait at the same time
        return url

    async def main():
        global barrier
        barrier = asyncio.Barrier(3)
        return await asyncio.wait_for(fetch_all(job, ["x", "y", "z"]), timeout=5)

    assert asyncio.run(main()) == ["x", "y", "z"], "fetches must run at the same time, not one by one"


def test_fetch_all_safe():
    out = asyncio.run(fetch_all_safe(fake, ["a", "bad", "c"]))
    assert out == [("a", "A"), ("bad", None), ("c", "C")]


def test_fetch_all_safe_empty():
    assert asyncio.run(fetch_all_safe(fake, [])) == []

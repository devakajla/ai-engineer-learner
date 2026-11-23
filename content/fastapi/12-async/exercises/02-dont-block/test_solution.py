import asyncio
import time

import httpx

from solution import app


async def hit(paths):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        return await asyncio.gather(*(client.get(p) for p in paths))


def test_reports_run_concurrently():
    start = time.perf_counter()
    responses = asyncio.run(hit([f"/report/{i}" for i in range(4)]))
    elapsed = time.perf_counter() - start
    assert [r.json()["user_id"] for r in responses] == [0, 1, 2, 3]
    assert elapsed < 0.8, f"4 requests took {elapsed:.2f}s — the event loop is blocked"


def test_health_stays_fast_during_reports():
    async def scenario():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            report = asyncio.create_task(client.get("/report/1"))
            await asyncio.sleep(0.05)
            start = time.perf_counter()
            health = await client.get("/health")
            fast = time.perf_counter() - start
            await report
            return health, fast

    health, fast = asyncio.run(scenario())
    assert health.json() == {"status": "ok"}
    assert fast < 0.15, "health must not wait for the report"

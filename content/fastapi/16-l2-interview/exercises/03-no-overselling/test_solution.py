import asyncio
from collections import Counter

import httpx

import solution
from solution import app

# One event loop for the whole module, like a real server process (asyncio locks belong to one loop).
LOOP = asyncio.new_event_loop()


def run(coro):
    return LOOP.run_until_complete(coro)


def setup_function():
    solution.STOCK.clear()
    solution.STOCK.update({"tshirt": 5, "mug": 3})


async def burst(path, n):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
        return await asyncio.gather(*(client.post(path) for _ in range(n)))


def test_no_overselling():
    responses = run(burst("/reserve/tshirt", 20))
    codes = Counter(r.status_code for r in responses)
    assert codes == {200: 5, 409: 15}, f"got {dict(codes)} — the check and the decrement must be atomic"
    assert solution.STOCK["tshirt"] == 0
    assert sorted(r.json()["remaining"] for r in responses if r.status_code == 200) == [0, 1, 2, 3, 4]


def test_items_independent_and_unknown():
    async def both():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://t") as client:
            return await asyncio.gather(
                *(client.post("/reserve/tshirt") for _ in range(5)),
                *(client.post("/reserve/mug") for _ in range(3)),
                client.post("/reserve/hat"),
            )

    responses = run(both())
    assert [r.status_code for r in responses[:8]] == [200] * 8
    assert responses[8].status_code == 404 and responses[8].json() == {"detail": "Unknown item"}
    sold_out = run(burst("/reserve/mug", 1))[0]
    assert sold_out.status_code == 409 and sold_out.json() == {"detail": "Sold out"}

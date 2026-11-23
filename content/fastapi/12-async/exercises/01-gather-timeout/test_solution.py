import asyncio
import inspect
import time

from fastapi.testclient import TestClient

from solution import app, fetch_all, prices


def test_concurrent():
    start = time.perf_counter()
    result = asyncio.run(fetch_all(["A", "BB", "CCC", "D", "E"]))
    elapsed = time.perf_counter() - start
    assert result == {"A": 1.0, "BB": 2.0, "CCC": 3.0, "D": 1.0, "E": 1.0}
    assert list(result) == ["A", "BB", "CCC", "D", "E"]
    assert elapsed < 0.6, f"took {elapsed:.2f}s — run the calls concurrently with asyncio.gather"


def test_timeout():
    start = time.perf_counter()
    assert asyncio.run(fetch_all(["A", "SLOW"])) == {"A": 1.0, "SLOW": None}
    assert time.perf_counter() - start < 1.5


def test_route():
    assert inspect.iscoroutinefunction(prices), "the route should be async def"
    r = TestClient(app).get("/prices?symbols=AAPL,MSFT")
    assert r.json() == {"AAPL": 4.0, "MSFT": 4.0}

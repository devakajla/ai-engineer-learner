import asyncio

from fastapi import FastAPI

app = FastAPI()


async def fetch_price(symbol: str) -> float:
    await asyncio.sleep(5 if symbol == "SLOW" else 0.2)
    return float(len(symbol))


async def _with_timeout(symbol: str, timeout: float) -> float | None:
    try:
        return await asyncio.wait_for(fetch_price(symbol), timeout)
    except TimeoutError:
        return None


async def fetch_all(symbols: list[str], timeout: float = 0.5) -> dict[str, float | None]:
    prices = await asyncio.gather(*(_with_timeout(s, timeout) for s in symbols))
    return dict(zip(symbols, prices, strict=True))


@app.get("/prices")
async def prices(symbols: str):
    return await fetch_all([s for s in symbols.split(",") if s])

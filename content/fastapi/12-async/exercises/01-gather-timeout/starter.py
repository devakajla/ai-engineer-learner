import asyncio

from fastapi import FastAPI

app = FastAPI()


async def fetch_price(symbol: str) -> float:
    await asyncio.sleep(5 if symbol == "SLOW" else 0.2)
    return float(len(symbol))


async def fetch_all(symbols, timeout=0.5):
    result = {}
    for s in symbols:
        result[s] = await fetch_price(s)
    return result

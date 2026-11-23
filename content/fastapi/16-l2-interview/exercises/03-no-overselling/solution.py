import asyncio
from collections import defaultdict

from fastapi import FastAPI, HTTPException

app = FastAPI()

STOCK = {"tshirt": 5}
_locks: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)


async def hold_payment() -> None:
    await asyncio.sleep(0.01)   # pretend to call the payment provider


@app.post("/reserve/{item}")
async def reserve(item: str):
    if item not in STOCK:
        raise HTTPException(404, "Unknown item")
    async with _locks[item]:          # check-and-decrement is now atomic for this item
        if STOCK[item] <= 0:
            raise HTTPException(409, "Sold out")
        await hold_payment()
        STOCK[item] -= 1
        return {"item": item, "remaining": STOCK[item]}

import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


def build_report(user_id: int) -> dict:
    time.sleep(0.3)          # blocking I/O in some library
    return {"user_id": user_id, "rows": 42}


@app.get("/report/{user_id}")
async def report(user_id: int):
    return build_report(user_id)

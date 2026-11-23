import asyncio


async def retry_async(fn, attempts=3, base_delay=0.5, retry_on=(Exception,), sleep=asyncio.sleep):
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    for attempt in range(1, attempts + 1):
        try:
            return await fn()
        except retry_on:
            if attempt == attempts:
                raise
            await sleep(base_delay * 2 ** (attempt - 1))

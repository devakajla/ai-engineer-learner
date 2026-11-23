import asyncio


async def retry_async(fn, attempts=3, base_delay=0.5, retry_on=(Exception,), sleep=asyncio.sleep):
    ...

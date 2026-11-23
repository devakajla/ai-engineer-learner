import asyncio


async def call_with_timeout(fn, seconds, default=None):
    try:
        async with asyncio.timeout(seconds):
            return await fn()
    except TimeoutError:
        return default


async def stream_words(text):
    for word in text.split():
        await asyncio.sleep(0)
        yield word


async def collect(agen):
    return [item async for item in agen]

import asyncio


async def limited_gather(fn, items, limit):
    if limit < 1:
        raise ValueError("limit must be at least 1")
    sem = asyncio.Semaphore(limit)

    async def run(item):
        async with sem:
            return await fn(item)

    return list(await asyncio.gather(*[run(item) for item in items]))

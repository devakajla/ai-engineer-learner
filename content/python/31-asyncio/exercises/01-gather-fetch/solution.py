import asyncio


async def fetch_all(fetch, urls):
    return list(await asyncio.gather(*[fetch(url) for url in urls]))


async def fetch_all_safe(fetch, urls):
    results = await asyncio.gather(*[fetch(url) for url in urls], return_exceptions=True)
    return [
        (url, None if isinstance(result, Exception) else result)
        for url, result in zip(urls, results)
    ]

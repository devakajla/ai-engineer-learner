# Limit how many run at once

Write `async def limited_gather(fn, items, limit)`:

- Run `await fn(item)` for every item, but **never more than `limit` at the same time**.
- Return the results in the same order as `items`.
- If `limit < 1`, raise `ValueError`.

```python
async def work(x):
    await asyncio.sleep(0)
    return x * 2

asyncio.run(limited_gather(work, [1, 2, 3, 4, 5], limit=2))   # -> [2, 4, 6, 8, 10]
```

**Think first:** How can 100 tasks be started, but only 3 be inside the work at one time?

**Hint:** Create an `asyncio.Semaphore(limit)` inside the function. Write a small inner `async def` that does `async with sem:` and then awaits `fn(item)`. Then `gather` them all.

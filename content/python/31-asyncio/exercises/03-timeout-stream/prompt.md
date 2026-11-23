# Timeouts and streaming

Write three things:

1. `async def call_with_timeout(fn, seconds, default=None)` – `await fn()` and return its result. If it takes longer than `seconds`, return `default` instead.
2. `async def stream_words(text)` – an **async generator** that yields the words of `text` one by one (split on spaces). Put `await asyncio.sleep(0)` before each `yield`, as a pause where other tasks can run.
3. `async def collect(agen)` – read any async generator with `async for` and return all items as a list.

```python
async def never():
    await asyncio.Event().wait()      # waits forever

asyncio.run(call_with_timeout(never, 0.01, default="late"))      # -> "late"
asyncio.run(collect(stream_words("a b c")))                      # -> ["a", "b", "c"]
```

**Think first:** What does `asyncio.timeout` raise when time runs out? Where must you catch it?

**Hint:** Wrap `async with asyncio.timeout(seconds):` in `try` / `except TimeoutError`. A function with both `async def` and `yield` is an async generator.

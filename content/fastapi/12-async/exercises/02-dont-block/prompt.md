# Don't block the event loop

This app has a bug that only shows under load: `/report` is `async def` but calls a **blocking** function, so concurrent requests run one after another.

Fix it **without changing `build_report`** (pretend it's a third-party library). Two valid fixes:

- make the route a plain `def` (FastAPI runs it in a thread pool), or
- keep `async def` and call `await asyncio.to_thread(build_report, user_id)`

Also add `GET /health` (async) that must stay fast even while reports are being built.

The tests fire 4 requests **concurrently**; with the bug they take ~1.2 s, fixed they take ~0.3 s.

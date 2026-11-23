---
title: Async endpoints & the event loop
summary: When async helps, how the event loop works, how to never block it, how to run calls at the same time, and async SQLAlchemy.
plan_ids: [FA-03, PY-08, PY-09]
---

AI backends spend most of their time **waiting**: for the database, for Redis, for an AI model API that takes 5 seconds to answer.

**Async** lets one process handle thousands of requests while they wait. But if you use it wrongly, your server becomes **slower** than plain code. This lesson gives you just enough asyncio to use it correctly in FastAPI. (The Python track's asyncio lesson goes deeper.)

## Concurrency and parallelism

These two words are not the same.

- **Parallelism**: doing several things at the **same instant**, using several CPU cores.
- **Concurrency**: making progress on several things by **switching between them while one is waiting**.

Think of one cook with three pots. The cook does not cook all three at the same instant. While pot 1 boils, the cook stirs pot 2. That is concurrency.

Async gives you concurrency on **one thread**. It is great for **I/O-bound** work, where the program mostly waits (network, disk, database). It does **not** speed up **CPU-bound** work, where the program is busy computing (heavy math, image processing).

## The event loop in 30 seconds

```python
import asyncio

async def fetch(name):
    await asyncio.sleep(1)       # pretend: waiting for the network
    return name

async def main():
    results = await asyncio.gather(fetch("a"), fetch("b"), fetch("c"))
    print(results)               # -> ['a', 'b', 'c']   (took about 1 second, not 3)

asyncio.run(main())
```

What is going on:

- `async def` makes a **coroutine function**. Calling it does not run it yet. It gives back a coroutine object.
- `await` runs a coroutine, and **pauses this function** until it is done. While it is paused, the **event loop** is free to run other work.
- The **event loop** is one thread that juggles many coroutines. It can switch only at an `await`. This is called **cooperative multitasking**: each coroutine must give control back politely.
- `asyncio.gather(...)` starts several coroutines at the same time and waits for all of them.

## How FastAPI runs your routes

You saw in lesson 2 that a route can be `def` or `async def`. Now you can see the real difference:

```python
@app.get("/sync")
def sync_route():              # FastAPI runs it in a THREAD POOL
    time.sleep(1)              # blocks only that one thread: fine
    return {}

@app.get("/async")
async def async_route():       # FastAPI runs it ON the event loop
    await asyncio.sleep(1)     # gives control back to the loop: fine
    return {}

@app.get("/broken")
async def broken():            # on the event loop...
    time.sleep(1)              # ...and this BLOCKS it. No other request runs for 1 second!
    return {}
```

Inside `async def`, the code runs on the single event loop thread. If it does something slow **without** `await`, the whole loop is stuck. Every other request waits.

The golden rule:

| Inside your route, you call... | So write the route as... |
|---|---|
| async libraries (`await client.get(...)` in httpx, async SQLAlchemy, async Redis) | `async def` |
| blocking libraries (`requests`, sync database drivers, `time.sleep`, heavy file work) | plain `def` |
| a blocking call you cannot avoid, inside `async def` | `await asyncio.to_thread(fn, ...)` |
| heavy CPU work | a separate process or a background worker (Level 3) |

One blocking call inside an `async def` route can stall **all** requests on that worker. It is the most common FastAPI speed bug.

`asyncio.to_thread(fn, arg)` runs a normal function in a helper thread, so the loop stays free:

```python
import asyncio, time

def slow_report(user_id):          # a blocking function you cannot change
    time.sleep(0.2)
    return {"user": user_id}

@app.get("/report/{user_id}")
async def report(user_id: int):
    return await asyncio.to_thread(slow_report, user_id)
```

## Calling things at the same time

If a route needs three independent things, do not wait for them one by one. Start them together with `gather`:

```python
async def get_dashboard(user_id):
    user, tasks, stats = await asyncio.gather(
        fetch_user(user_id),
        fetch_tasks(user_id),
        fetch_stats(user_id),
    )
```

Three calls of 200 ms each take about **200 ms** in total, not 600 ms.

Always add a **timeout** to outside calls, so one slow service cannot hang your route. `asyncio.wait_for` gives up after some seconds and raises `TimeoutError`:

```python
try:
    price = await asyncio.wait_for(fetch_price("AAPL"), timeout=2.0)
except TimeoutError:
    price = None
```

## Worked example: many calls, with a timeout for each

Exercise 1 asks you to fetch many prices at the same time, and to give `None` for any call that is too slow. Here is the same pattern for a different problem: **weather by city**.

The given function (it pretends to call a weather service):

```python
async def fetch_temp(city):
    await asyncio.sleep(5 if city == "Slowville" else 0.1)
    return 25.0
```

Goal: `fetch_temps(cities, timeout=0.5)` returns a dict `{city: temperature or None}`, fast.

**Step 1.** Write a helper for **one** city. It has the timeout and turns a timeout into `None`.

```python
async def one(city, timeout):
    try:
        return await asyncio.wait_for(fetch_temp(city), timeout=timeout)
    except TimeoutError:
        return None
```

**Step 2.** Start the helper for **every** city with `gather`. `gather` returns results in the same order as its inputs.

```python
async def fetch_temps(cities, timeout=0.5):
    results = await asyncio.gather(*(one(c, timeout) for c in cities))
    return dict(zip(cities, results))
```

`*(...)` unpacks the generator into separate arguments. `zip` pairs each city with its result.

**Step 3.** Run it and look at the time.

```python
import time

async def main():
    start = time.perf_counter()
    print(await fetch_temps(["Pune", "Goa", "Slowville"]))
    # -> {'Pune': 25.0, 'Goa': 25.0, 'Slowville': None}
    print(round(time.perf_counter() - start, 1))   # -> 0.5

asyncio.run(main())
```

The two fast cities and the slow one run together. The whole thing takes about 0.5 seconds (the timeout), not 5.2.

**Step 4.** Use it in an `async` route. Split a text like `"Pune,Goa"` with `split(",")`.

```python
@app.get("/temps")
async def temps(cities: str):
    return await fetch_temps(cities.split(","))
```

## Async HTTP calls

For web calls inside async code, use `httpx` with its async client:

```python
import httpx

async with httpx.AsyncClient(timeout=10) as client:
    response = await client.get("https://api.example.com/data")
```

In a real app, create **one** `AsyncClient` when the app starts (in the lifespan) and reuse it, because it keeps connections open for speed. Never use `requests` inside `async def`: it is blocking.

## Async SQLAlchemy

SQLAlchemy has an async version. The idea is the same as lesson 10, but each database call is awaited.

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine("sqlite+aiosqlite:///./taskflow.db")
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as session:
        yield session

@router.get("/{task_id}")
async def get_task(task_id: int, db: Annotated[AsyncSession, Depends(get_db)]):
    task = await db.get(Task, task_id)
    tasks = (await db.scalars(select(Task).limit(20))).all()
    db.add(Task(title="x"))
    await db.commit()
```

How it differs from the sync version:

- Every database round trip is awaited: `execute`, `scalars`, `get`, `commit`, `refresh`, `delete`.
- The driver must be async too: `aiosqlite` for SQLite, `asyncpg` for Postgres. The address changes to `sqlite+aiosqlite://...` or `postgresql+asyncpg://...`.
- **Lazy loading does not work.** Touching an unloaded relationship (like `user.tasks`) would need a hidden `await`, so it raises an error (`MissingGreenlet`). Load relationships up front with `selectinload(...)` (lesson 10).
- `expire_on_commit=False` keeps objects readable after a commit.
- Creating tables uses `await conn.run_sync(Base.metadata.create_all)` inside `async with engine.begin() as conn:`.

## Should everything be async?

Not always. Async pays off when your app does a lot of **waiting on many things at once**: AI model calls, many database queries, streaming, WebSockets. A simple CRUD API with a sync driver and `def` routes is perfectly fine, and simpler.

What matters is being **consistent**: do not hide blocking calls inside async code.

## A little deeper (optional)

- `asyncio.gather(..., return_exceptions=True)` returns errors as values in the result list, instead of failing everything at once.
- Python 3.11 added `asyncio.TaskGroup`, a safer way to start several tasks together. It cancels the rest if one fails.
- FastAPI's thread pool for `def` routes has a limit (about 40 threads by default). Many slow blocking requests can use them all up.
- Forgetting `await` gives a coroutine object instead of a result, and a warning "coroutine was never awaited". Nothing ran.

## Common mistakes

- Using `time.sleep`, `requests.get`, or sync database calls inside `async def`.
- Forgetting `await`.
- Awaiting calls one after another when they could run together with `gather`.
- No timeout on outside calls.
- Using lazy-loaded relationships with `AsyncSession`.

## Interview corner

- **Q: When is a route `async def`, and when `def`?** Use `async def` only if everything slow inside is awaited async I/O. Otherwise use `def`, and FastAPI runs it in a thread pool.
- **Q: What happens if you call `time.sleep(2)` in an `async def` route?** It blocks the event loop. Every request on that worker waits 2 seconds.
- **Q: How do you call three services at the same time?** `asyncio.gather` (or a `TaskGroup`), with timeouts.
- **Q: Does async make CPU-heavy code faster?** No. It runs on one thread. Use processes or workers for CPU work.

## Summary

- Async gives concurrency for I/O on one thread. It switches only at `await`.
- `def` routes run in a thread pool. `async def` routes run on the event loop. Never block the loop.
- Use `asyncio.gather` with `wait_for` timeouts. Use `asyncio.to_thread` for blocking calls you cannot avoid.
- Async SQLAlchemy: `create_async_engine`, `AsyncSession`, `await` every call, and load relationships up front.

# 9. Async endpoints and the event loop

In the last chapter we wrote `async def` and `await` and kept going. This chapter explains what they mean, **when they help**, and the one mistake that can freeze your whole server.

## Idea: waiting is wasted time

Most of a backend's time is spent **waiting**: for the database, for another API, for a file. While one request waits, the CPU sits idle.

Real life: a cook puts a pot on the stove. Does he stand and stare at the pot for 10 minutes? No. He chops onions meanwhile. That is **async**: while one task waits, run another one.

Python's tool for this is the **event loop**. It is one worker who keeps a list of tasks. When a task says "I am waiting" (`await`), the loop switches to another task.

@@ flow | Figure 9.1: one thread serving three requests.
Request A|starts, then awaits the DB|blue -> Request B|runs while A waits|green -> Request C|runs while B waits|yellow -> Request A|DB answered, finishes|blue
@@ end

## Proof with numbers

Create a scratch file `scratch.py` (outside `app/`) and run it with `uv run python scratch.py`:

```python
import asyncio
import time


async def fetch(n):
    await asyncio.sleep(1)       # pretend: a slow database call
    return n * 2


async def main():
    t = time.perf_counter()
    a = await fetch(1)
    b = await fetch(2)
    c = await fetch(3)
    print("one by one:", [a, b, c], round(time.perf_counter() - t, 1), "s")
    # -> one by one: [2, 4, 6] 3.0 s

    t = time.perf_counter()
    results = await asyncio.gather(fetch(1), fetch(2), fetch(3))
    print("gather:", results, round(time.perf_counter() - t, 1), "s")
    # -> gather: [2, 4, 6] 1.0 s


asyncio.run(main())
```

Three one-second waits take **3 seconds in a row**, but **1 second together** with `gather`. Nothing ran in parallel on the CPU. The waits **overlapped**.

New words:

| Word | Meaning |
| --- | --- |
| `async def` | defines a **coroutine**: a function that can pause |
| `await` | pause here until the result is ready, and let others run |
| `asyncio.gather(...)` | run several coroutines together and collect results |
| `asyncio.sleep(n)` | an async wait (does not block) |

You can only use `await` inside an `async def`.

## The deadly mistake: blocking the loop

If a task does slow work **without `await`**, the loop cannot switch. Everyone waits.

Make a scratch app, `blk.py`, with three routes that each take 2 seconds:

```python
import asyncio
import time

from fastapi import FastAPI

app = FastAPI()


@app.get("/bad")
async def bad():
    time.sleep(2)           # BLOCKS the whole event loop
    return {"route": "bad"}


@app.get("/good")
async def good():
    await asyncio.sleep(2)  # lets other requests run
    return {"route": "good"}


@app.get("/sync")
def sync_route():
    time.sleep(2)           # runs in a worker thread, so it is fine
    return {"route": "sync"}
```

Run it with `uv run uvicorn blk:app --port 8011`. In another terminal, send 3 requests **at the same time** and time them:

```bash
for r in bad good sync; do
  echo $r
  time (curl -s localhost:8011/$r >/dev/null & curl -s localhost:8011/$r >/dev/null & curl -s localhost:8011/$r >/dev/null & wait)
done
```

Real results on one machine:

| Route | 3 requests at once took | Why |
| --- | --- | --- |
| `/bad` (`async def` + `time.sleep`) | **6 s** (2 + 2 + 2, one after another) | the loop was blocked |
| `/good` (`async def` + `await asyncio.sleep`) | **2 s** | the waits overlapped |
| `/sync` (`def` + `time.sleep`) | **2 s** | FastAPI runs `def` routes in a thread pool |

`/bad` is the dangerous one. While it sleeps, **every other request** to your server, even `/health`, waits.

## The rule

@@ grid 2 | Figure 9.2: choosing `def` or `async def`.
Use async def|when everything slow inside uses await;async DB driver, httpx.AsyncClient, asyncio.sleep|green
Use plain def|when you must call blocking code;requests, time.sleep, a normal DB driver, heavy file work|yellow
@@ end

> **Never put blocking code inside `async def`.** If you are not sure, use plain `def`. It is safe, because FastAPI moves it to a thread.

Common blocking things to avoid inside `async def`: `time.sleep`, the `requests` library, a normal (sync) database driver, reading huge files, and long CPU loops.

## Calling other services the async way

Use `httpx.AsyncClient` instead of `requests`:

```python
import httpx

async def get_joke():
    async with httpx.AsyncClient(timeout=5) as client:
        response = await client.get("https://example.com/api")
        response.raise_for_status()
        return response.json()
```

Always set a **timeout**. Without one, a slow service can hold your request forever.

## Running calls together, with limits

To call several services at once, `gather` them. To avoid overload, limit how many run at the same time with a **semaphore**:

```python
sem = asyncio.Semaphore(2)          # at most 2 at a time

async def limited(n):
    async with sem:
        return await fetch(n)

results = await asyncio.gather(*(limited(i) for i in range(4)))
# 4 tasks, 2 at a time, each 1 s  ->  2.0 s total
```

And add a time limit to anything that could hang:

```python
try:
    result = await asyncio.wait_for(fetch(1), timeout=0.5)
except asyncio.TimeoutError:
    print("too slow")
```

## CPU-heavy work

`async` helps with **waiting**. It does **not** speed up heavy calculation (resizing an image, parsing a huge file). That blocks the loop too. For CPU-heavy work, use a **queue and a worker** (chapter 12) or a separate process.

If you must do a small blocking job inside an async route, move it to a thread:

```python
from fastapi.concurrency import run_in_threadpool

@app.get("/report")
async def report():
    data = await run_in_threadpool(build_big_report)   # a normal blocking function
    return data
```

## Our own code

All of TaskFlow's routes are `async def` and use `await` on an **async** database driver (`aiosqlite`, later `asyncpg`). That is correct. The path is: route (`async`) → service (`async`) → repository (`async`) → driver (non-blocking). Every layer awaits the next. **One blocking call anywhere in that chain breaks the benefit.**

::: {.box .checkpoint}
**Folder now:** no change in `app/`. You wrote two scratch files, `scratch.py` and `blk.py`. Delete them or keep them in a `scratch/` folder that is git-ignored.

**Checkpoint:** you saw `/bad` take about 6 seconds for 3 requests and `/good` about 2 seconds, and you can explain why.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- `time.sleep()` or the `requests` library inside `async def`.
- Using a sync database driver with `async def` routes.
- Forgetting `await`, so the coroutine never runs. (You see a warning: `coroutine ... was never awaited`.)
- Thinking `async` makes code faster. It lets **waiting** overlap. It does not speed up calculation.
- No timeouts on outgoing calls.
- Starting 10,000 tasks at once with `gather` and overwhelming a service. Use a semaphore.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is the difference between `def` and `async def` routes in FastAPI?**
`async def` runs on the event loop and must not block. Plain `def` runs in a thread pool, so blocking code is safe there.

**Q: What does `await` do?**
It pauses the current coroutine until the result is ready, and lets the event loop run other tasks meanwhile.

**Q: What happens if you call `time.sleep` in an `async def` route?**
It blocks the event loop, so all requests on that worker freeze.

**Q: When does async not help?**
For CPU-bound work. Use processes or a task queue.

**Q: Concurrency vs parallelism?**
Concurrency means many tasks make progress by taking turns (async, threads). Parallelism means tasks run at the same instant on multiple CPU cores (processes).
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. In `scratch.py`, add a fourth `fetch` to the `gather`. How long does it take? Why?
2. Add `/bad2` that uses `await asyncio.sleep(2)` inside `async def`, and compare with `/bad`. Explain the difference in your own words.
3. Use `asyncio.wait_for` with a timeout of 1 second around a function that sleeps 3 seconds. What error do you get?
4. Use a `Semaphore(3)` to run 9 one-second tasks. How long should it take? Check.
5. **Think:** your route calls a library that has only a blocking version. Name two ways to use it safely.
:::

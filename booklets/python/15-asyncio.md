# 15. asyncio in depth

`asyncio` is Python's way of doing many waiting jobs at once on **one thread**. FastAPI, the Groq and OpenAI async clients, and most modern AI backends are built on it. If you understand this chapter well, async code stops feeling like magic.

## The mental model: one cook, many pots

A single cook (the **event loop**) looks after many pots (tasks). Whenever a pot just needs to simmer (waiting for a network reply), the cook does not stand and stare. The cook moves to another pot. When the first pot is ready, the cook comes back.

Nothing runs at the same *instant*. The jobs **take turns**, and a job gives up its turn only at a special word: **`await`**. That is why it is called **cooperative**.

@@ flow | Figure 15.1: the event loop switches at every await.
Task A|runs until it hits await|blue -> Task B|runs while A waits|green -> Task C|runs while B waits|yellow -> Task A|its data arrived;continues|blue
@@ end

## The three words

- `async def` makes a **coroutine function**. Calling it does **not** run it. It returns a coroutine object, a job waiting to be started.
- `await x` means "pause me until `x` is done, and let others run". It works only inside `async def`.
- `asyncio.run(main())` starts the event loop and runs your top-level coroutine. You call it once, at the bottom of your program.

```python
import asyncio

async def fetch(n):
    await asyncio.sleep(1)      # a pretend network call
    return n * 2

async def main():
    print(await fetch(1))

asyncio.run(main())
# -> 2
```

`asyncio.sleep` is the **async** way to wait. Compare with `time.sleep`, which freezes the whole thread (and so the whole loop). That difference is the heart of everything below.

## Running things together: `gather`

Awaiting one by one is no faster than normal code. The gain comes from starting many at once:

```python
import time

async def main():
    start = time.perf_counter()
    results = await asyncio.gather(fetch(1), fetch(2), fetch(3))
    print(results, round(time.perf_counter() - start, 1))

asyncio.run(main())
# -> [2, 4, 6] 1.0
```

Three jobs of one second each took **one** second, since all three waited at the same time. `gather` returns results in the order you gave the jobs.

## Tasks: start now, await later

`asyncio.create_task(coro)` schedules a coroutine to run **in the background** and gives you a task object. You continue, and `await` it when you need the result.

```python
async def main():
    task = asyncio.create_task(fetch(5))
    print("meanwhile")
    print(await task)

# -> meanwhile
# -> 10
```

"meanwhile" printed first, because the task only began running when `main` reached an `await`. Use `gather` when you want a group of results. Use `create_task` for work you want to start early or run in the background.

## Timeouts

Never wait forever for something outside your control. `wait_for` raises `TimeoutError` when time is up:

```python
async def main():
    try:
        await asyncio.wait_for(fetch(1), timeout=0.1)
    except asyncio.TimeoutError:
        print("timeout")

# -> timeout
```

`wait_for` also **cancels** the slow job for you.

## Limiting concurrency: `Semaphore`

Starting 10,000 requests at once will overload a server or hit a rate limit. A **semaphore** is a gate with N places. Only N tasks pass at one time, and the rest wait their turn.

```python
sem = asyncio.Semaphore(2)

async def limited(n):
    async with sem:
        return await fetch(n)

async def main():
    start = time.perf_counter()
    await asyncio.gather(*(limited(i) for i in range(4)))
    print(round(time.perf_counter() - start, 1))

# -> 2.0
```

Four one-second jobs, two at a time: two rounds, so 2 seconds. This is how you call an LLM API many times without breaking its rate limit.

## Cancellation

Any task can be cancelled. The task receives a `CancelledError` at its next `await`.

```python
async def main():
    task = asyncio.create_task(fetch(1))
    await asyncio.sleep(0.1)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        print("cancelled")

# -> cancelled
```

This is what happens when a web client disconnects mid-request. Good code uses `try/finally` to clean up when cancelled.

## Errors in groups

By default `gather` raises the **first** error, though the other tasks keep running. To collect every outcome, pass `return_exceptions=True`:

```python
async def broken():
    raise ValueError("x")

async def main():
    print(await asyncio.gather(fetch(1), broken(), return_exceptions=True))

# -> [2, ValueError('x')]
```

The modern, safer way (Python 3.11 and newer) is a **TaskGroup**. If one task fails, it cancels the others, and leaving the block waits for all of them:

```python
async def main():
    async with asyncio.TaskGroup() as group:
        a = group.create_task(fetch(1))
        b = group.create_task(fetch(2))
    print(a.result(), b.result())

# -> 2 4
```

Prefer `TaskGroup` for new code, since no task is left running by accident.

## The big mistake: blocking the loop

If one task does slow work **without** `await`, the cook is stuck at that pot. Every other task freezes.

```python
async def bad():
    time.sleep(2)          # blocks the whole loop
```

In a FastAPI test, three parallel requests to such a route took **6 seconds** (2 + 2 + 2). With `await asyncio.sleep(2)` they took **2 seconds**. Common blockers: `time.sleep`, the `requests` library, normal file reads on big files, and heavy loops.

Fix: use an async library (`httpx.AsyncClient`, async database drivers), or push blocking work to a thread:

```python
async def main():
    await asyncio.to_thread(time.sleep, 0.2)   # runs in a thread, the loop stays free
```

## Async iteration and context managers

`async for` loops over something that produces items asynchronously, such as a stream of tokens from an LLM. `async with` is a context manager whose setup and cleanup are async, such as an HTTP client.

```python
async def tokens():
    for word in ["Hel", "lo"]:
        await asyncio.sleep(0.1)
        yield word                 # an async generator

async def main():
    async for t in tokens():
        print(t, end="")

# -> Hello
```

An `async def` that uses `yield` is an **async generator**, the async cousin of chapter 10. This is how streaming responses are built.

## A queue between tasks

`asyncio.Queue` lets a producer hand work to a consumer safely:

```python
async def main():
    queue = asyncio.Queue()

    async def producer():
        for i in range(3):
            await queue.put(i)
        await queue.put(None)         # a signal: no more items

    async def consumer():
        while (item := await queue.get()) is not None:
            print("got", item)

    await asyncio.gather(producer(), consumer())

# -> got 0
# -> got 1
# -> got 2
```

This is a tiny version of a worker queue. Real systems use Redis or a broker, but the shape is the same.

## Decision guide

| Situation | Do this |
| --- | --- |
| many network calls | `async` + `gather` / `TaskGroup` |
| must not overload a server | add a `Semaphore` |
| might hang | `wait_for` with a timeout |
| library is blocking | `asyncio.to_thread` |
| heavy CPU work | a process pool or worker queue |

::: {.box .checkpoint}
**Checkpoint:** you can explain why `await` is the only place tasks switch, why `time.sleep` is harmful in `async def`, and how a Semaphore of 2 changes the timing of four jobs.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Calling an `async def` function and forgetting `await`. You get a coroutine object and a warning.
- Blocking calls inside `async def`.
- Awaiting jobs one after another when they could run together.
- No timeouts on network calls.
- Starting unlimited concurrent tasks.
- Calling `asyncio.run` inside code that is already running in an event loop.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is the event loop?** The scheduler that runs coroutines and switches between them whenever one awaits.

**Q: `gather` vs `create_task`?** `gather` runs several awaitables and collects their results. `create_task` starts one in the background and returns a handle.

**Q: Why not use `time.sleep` in async code?** It blocks the whole thread and therefore every task on the loop.

**Q: Does async make code faster?** It makes **waiting** overlap. It does not speed up calculation.

**Q: How do you limit concurrency?** An `asyncio.Semaphore`.

**Q: What happens if a task is cancelled?** It gets `CancelledError` at its current `await`. Use `finally` for cleanup.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Run five `fetch` calls one by one, then with `gather`. Compare the times.
2. Use a `Semaphore(3)` with 9 jobs of one second. Predict the time, then check.
3. Add a timeout of 0.5 s to a job that takes 2 s. Handle the error.
4. Use `gather(..., return_exceptions=True)` with one failing job and print the result list.
5. Write an async generator that yields 5 numbers with a short wait, and consume it with `async for`.
6. **Think:** why does `await asyncio.sleep(1)` let other tasks run, but `time.sleep(1)` does not?
:::

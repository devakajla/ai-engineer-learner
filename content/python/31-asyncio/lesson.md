---
title: asyncio in depth
summary: Run thousands of waiting tasks on one thread with async and await, and learn gather, tasks, timeouts, limits and async generators.
plan_ids: [PY-08]
---

In the last lesson, threads helped with waiting. But a thread costs memory, and a program with thousands of connections cannot have thousands of threads. **asyncio** is another way: one thread runs **many tasks**, and a task steps aside whenever it has to wait. FastAPI is built on this, and so are most AI API clients.

## The big idea

A cook in a kitchen puts the rice on the stove. While it cooks, the cook does not stand and watch it. The cook chops vegetables. The cook gives attention to each thing **only when it needs it**.

asyncio works the same way:

- One thread. One **event loop** that decides which task runs next.
- A task runs until it reaches an `await`. That is a place where it says "I am waiting, someone else can run".
- When the thing it waits for is ready, the loop continues that task.

## `async def` and `await`

A function written with `async def` is a **coroutine function**. Calling it does **not** run it. It gives you a **coroutine object**, a plan that has not started. You run it with `await`, or with `asyncio.run(...)` at the top.

```python
import asyncio

async def greet(name):
    await asyncio.sleep(0.1)       # wait without blocking the others
    return f"hello {name}"

async def main():
    message = await greet("Dev")
    print(message)                 # -> hello Dev

asyncio.run(main())
```

- `await` can be used **only inside** an `async def` function.
- `asyncio.run(main())` starts the event loop, runs `main`, and closes the loop. Call it once, at the top of the program.
- Forget the `await`, and you get a coroutine object that never ran (and Python warns you):

```python
async def main():
    greet("Dev")          # WRONG: the coroutine is created, but never run
```

> Use `asyncio.sleep`, never `time.sleep`, inside async code. `time.sleep` **blocks the whole loop**, and every other task freezes.

## Running tasks at the same time: `gather`

If you `await` two jobs one after the other, they run one after the other:

```python
async def main():
    a = await greet("a")      # waits 0.1 s
    b = await greet("b")      # waits another 0.1 s
```

To run them **together**, use `asyncio.gather`. It takes several coroutines, runs them at the same time, and returns the results in **the same order you gave them**.

A step-by-step example: look up three prices at the same time.

1. Write an `async def` function for one lookup.
2. Make a list of coroutines (call the function for each item, with no `await`).
3. `await asyncio.gather(*coroutines)`. The `*` unpacks the list into separate arguments.

```python
import asyncio

async def get_price(item):
    await asyncio.sleep(0.1)           # pretend this is a network call
    return {"apple": 3, "pear": 5, "fig": 8}[item]

async def main():
    items = ["apple", "pear", "fig"]
    prices = await asyncio.gather(*[get_price(i) for i in items])
    print(prices)                      # -> [3, 5, 8]

asyncio.run(main())                    # takes about 0.1 s, not 0.3 s
```

### When a job fails

By default, if one job raises an error, `gather` raises it, and you lose the other results. To keep going, pass `return_exceptions=True`. Then an error is **returned in the list** in place of a result:

```python
async def risky(x):
    if x == 0:
        raise ValueError("zero")
    return 10 // x

async def main():
    results = await asyncio.gather(risky(5), risky(0), risky(2), return_exceptions=True)
    print(results[0], results[2])               # -> 2 5
    print(isinstance(results[1], ValueError))   # -> True

asyncio.run(main())
```

## Tasks: start now, wait later

`asyncio.create_task(coro)` **starts** a coroutine right away in the background, and gives you a **task**. You can do other things, and `await` the task later to get its result.

```python
async def main():
    task = asyncio.create_task(greet("a"))     # starts running now
    print("doing other work")                  # -> doing other work
    print(await task)                          # -> hello a

asyncio.run(main())
```

Python 3.11 added **`asyncio.TaskGroup`**, which is a safer way to run a group of tasks. It waits for all of them when the `with` block ends. If one fails, the others are cancelled:

```python
async def main():
    async with asyncio.TaskGroup() as group:
        t1 = group.create_task(greet("a"))
        t2 = group.create_task(greet("b"))
    print(t1.result(), t2.result())            # -> hello a hello b

asyncio.run(main())
```

(`async with` is the async version of `with`, lesson 24.)

## Limiting how many run at once: `Semaphore`

If you start 1000 requests at once, the server may refuse you. A **semaphore** is like a number of tickets. Only that many tasks can be inside at the same time. The others wait for a ticket.

```python
async def limited(sem, item):
    async with sem:                    # take a ticket, give it back at the end
        await asyncio.sleep(0.1)
        return item * 2

async def main():
    sem = asyncio.Semaphore(2)         # at most 2 at a time
    results = await asyncio.gather(*[limited(sem, n) for n in [1, 2, 3, 4]])
    print(results)                     # -> [2, 4, 6, 8]

asyncio.run(main())
```

Make the semaphore **inside** `main` (inside the running loop), and share the same one with all tasks.

## Timeouts

Never wait for a network forever. `asyncio.timeout(seconds)` is a context manager. If the block takes longer, it raises `TimeoutError`:

```python
async def slow():
    await asyncio.sleep(10)

async def main():
    try:
        async with asyncio.timeout(0.1):
            await slow()
    except TimeoutError:
        print("too slow")               # -> too slow

asyncio.run(main())
```

(`asyncio.wait_for(coro, timeout)` does the same for a single coroutine.) When a timeout happens, the waiting task is **cancelled**: Python raises `asyncio.CancelledError` inside it. If you catch that, always raise it again, and use `finally` for cleanup.

## Async iteration: `async for` and async generators

An **async generator** is an `async def` function with `yield`. You read it with `async for`. It is perfect for **streaming**: giving out a piece at a time as it arrives, like the words of an AI answer.

```python
async def words(text):
    for word in text.split():
        await asyncio.sleep(0)          # a pause where other tasks can run
        yield word

async def main():
    out = []
    async for w in words("one two three"):
        out.append(w)
    print(out)                          # -> ['one', 'two', 'three']

asyncio.run(main())
```

An async list comprehension works too: `[w async for w in words("a b")]`.

In FastAPI, a `StreamingResponse` can take an async generator like this one.

## Do not block the loop

All tasks share one thread. If one task does slow work **without** `await`, every other task waits.

- A long calculation (CPU-bound) blocks the loop. Send it to a process pool (lesson 30).
- Old blocking code (a library with no async version) can go to a thread: `await asyncio.to_thread(function, arguments)` runs it in a thread and does not block the loop.

```python
import time

def slow_blocking(x):
    time.sleep(0.1)            # blocking code
    return x * 2

async def main():
    result = await asyncio.to_thread(slow_blocking, 21)
    print(result)              # -> 42

asyncio.run(main())
```

## Choosing between threads and asyncio

| | Threads | asyncio |
|---|---|---|
| Tasks | tens | thousands |
| Code style | normal functions | `async` / `await` everywhere |
| Switching | the system decides, at any moment | only at `await` |
| Locks needed | often | rarely (no switch between two lines without `await`) |
| Needs async libraries | no | yes |

If one function in the chain is `async`, the callers must be `async` too. This is sometimes called "async spreads".

## A little deeper (optional)

- **Cancellation.** `task.cancel()` raises `CancelledError` inside the task at its next `await`.
- **Queues.** `asyncio.Queue` is the async version of `queue.Queue`, for producer / consumer patterns.
- **Locks.** `asyncio.Lock` exists, for the rare case where two tasks must not run a section with an `await` in the middle at the same time.
- **`asyncio.run` in notebooks or inside a running loop** can fail, because a loop is already running. Use `await main()` there.

## Common mistakes

- Forgetting `await`. The coroutine never runs.
- Calling `time.sleep` or a blocking library inside `async def`.
- `await`-ing jobs one by one when they could run together with `gather`.
- Starting an unlimited number of tasks and overloading a server. Use a semaphore.
- No timeout on network calls.
- Catching `CancelledError` and not raising it again.

## Interview corner

- **Q: What is the event loop?** A loop that runs tasks. A task runs until it hits an `await`, then the loop runs another task.
- **Q: `gather` or `create_task`?** `gather` runs several coroutines together and gives all results in order. `create_task` starts one in the background so you can wait for it later.
- **Q: What happens if you call `time.sleep` in an async function?** It blocks the whole event loop, so every other task freezes. Use `await asyncio.sleep`.
- **Q: How do you limit concurrency?** An `asyncio.Semaphore`, used with `async with`.
- **Q: How do you run blocking code from async code?** `await asyncio.to_thread(...)`, or a process pool for CPU-bound work.

## Summary

- `async def` makes a coroutine. `await` runs it and waits. `asyncio.run` starts the loop.
- `gather` runs coroutines together and keeps the order. `return_exceptions=True` returns errors in the list.
- `create_task` and `TaskGroup` run tasks in the background.
- `Semaphore` limits how many run at once. `asyncio.timeout` stops long waits.
- Async generators and `async for` stream data.
- Never block the loop. Use `asyncio.sleep`, and `to_thread` for blocking code.

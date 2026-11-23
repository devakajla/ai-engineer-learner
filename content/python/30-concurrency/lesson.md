---
title: Concurrency & the GIL
summary: Do many things at the same time with threads and processes, and learn what the GIL is, when to use which, and how to avoid race conditions.
plan_ids: [PY-08]
---

Some programs spend most of their time **waiting**: for a web page, a file or a database. If the program waits for one thing at a time, it is slow. **Concurrency** means a program works on many things at once, so the waiting overlaps.

This lesson shows the tools Python gives you, and how to pick the right one.

## Two kinds of slow work

Before you choose a tool, ask: **why is this code slow?**

- **I/O-bound**: the program waits for the outside world (a network call, a disk, an AI API). The CPU is mostly idle.
- **CPU-bound**: the program is busy calculating (resizing images, heavy maths). The CPU is working all the time.

```python
import time

def wait_a_bit():            # I/O-bound: it only waits
    time.sleep(1)

def count_a_lot():           # CPU-bound: it works the whole time
    total = 0
    for i in range(10_000_000):
        total += i
    return total
```

The right tool depends on this question.

## Threads and processes

- A **thread** is a path of work inside your program. Many threads share the same memory.
- A **process** is a whole separate copy of your program, with its own memory.

| | Thread | Process |
|---|---|---|
| Memory | shared with other threads | its own |
| Cost to start | small | bigger |
| Good for | I/O-bound work | CPU-bound work |
| Danger | two threads changing the same data | passing data between processes is slower |

## The GIL

In the normal version of Python (CPython), there is a rule called the **GIL** (Global Interpreter Lock). It lets **only one thread run Python code at a time**.

What this means:

- For **I/O-bound** work, threads still help. A thread that is waiting lets go of the GIL, so another thread can run.
- For **CPU-bound** work, threads do **not** make the code faster. They take turns on one core.
- For CPU-bound work, use **processes**. Each process has its own GIL, so they can use many cores.

> Newer Python versions have an experimental "free-threaded" build without the GIL. The normal build still has it, and this lesson explains the normal one.

## `ThreadPoolExecutor`: the easy way to use threads

`concurrent.futures` gives you a **pool**: a group of workers that take jobs one by one. You do not manage the threads yourself.

`executor.map(function, items)` runs the function for every item, using the workers. The results come back **in the same order as the items**.

```python
from concurrent.futures import ThreadPoolExecutor

def double(x):
    return x * 2

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(double, [1, 2, 3, 4]))

print(results)     # -> [2, 4, 6, 8]
```

The `with` block (lesson 24) waits for all work to finish and cleans up the threads.

A step-by-step example. We want to "download" three pages at the same time. Each one takes one second. Done one by one, it takes three seconds. With threads, it takes about one second.

1. Write a function for one job.
2. Make a pool.
3. Use `map` to run the job for every item.
4. Read the results.

```python
import time
from concurrent.futures import ThreadPoolExecutor

def fetch(name):
    time.sleep(1)                 # pretend this is a slow download
    return f"page {name}"

start = time.perf_counter()
with ThreadPoolExecutor(max_workers=3) as executor:
    pages = list(executor.map(fetch, ["a", "b", "c"]))
elapsed = time.perf_counter() - start

print(pages)                      # -> ['page a', 'page b', 'page c']
print(elapsed < 2)                # -> True     about 1 second, not 3
```

### Futures: results that come later

`executor.submit(function, arguments)` starts one job and gives back a **future**: a promise of a result. Call `future.result()` to wait for it. If the job raised an error, `result()` raises that same error.

```python
with ThreadPoolExecutor(max_workers=2) as executor:
    future = executor.submit(double, 21)
    print(future.result())        # -> 42
```

To handle each result **as soon as it is ready** (not in order), use `as_completed`:

```python
from concurrent.futures import as_completed

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(double, n) for n in [1, 2, 3]]
    done = [f.result() for f in as_completed(futures)]

print(sorted(done))    # -> [2, 4, 6]     the order of `done` can change, so we sort
```

### Errors inside threads

An error inside a job does not crash your program at once. It is stored in the future. You see it when you call `result()`. A good habit is to catch it there:

```python
def risky(x):
    if x == 2:
        raise ValueError("bad item")
    return x

with ThreadPoolExecutor(max_workers=2) as executor:
    futures = [executor.submit(risky, n) for n in [1, 2, 3]]
    for f in futures:
        try:
            print("ok", f.result())
        except ValueError as e:
            print("failed:", e)
# -> ok 1
# -> failed: bad item
# -> ok 3
```

## Processes for CPU-bound work

`ProcessPoolExecutor` has the same interface, but each worker is a separate process:

```python
from concurrent.futures import ProcessPoolExecutor

def heavy(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":                # needed: each process re-imports the file
    with ProcessPoolExecutor() as executor:
        print(list(executor.map(heavy, [10**6, 10**6])))
```

Things to know:

- The function and its arguments must be **picklable** (turnable into bytes), because they are sent to the other process. Normal functions and simple data are fine. Lambdas are not.
- Starting a process is slower than starting a thread. It pays off only for heavy work.

## Race conditions and locks

When threads share data and **change** it, bad things can happen. Look at this:

```python
counter = 0

def add_many():
    global counter
    for _ in range(100_000):
        counter += 1
```

`counter += 1` looks like one step, but it is three: **read** the value, **add** 1, **write** it back. Two threads can read the same value, and one of the additions is lost. This is a **race condition**. The result changes from run to run.

The fix is a **lock**. Only one thread can hold it at a time. The others wait.

```python
import threading

counter = 0
lock = threading.Lock()

def add_many():
    global counter
    for _ in range(100_000):
        with lock:                    # only one thread inside at a time
            counter += 1

threads = [threading.Thread(target=add_many) for _ in range(4)]
for t in threads:
    t.start()
for t in threads:
    t.join()                          # wait until the thread finishes

print(counter)    # -> 400000    always right
```

- `threading.Thread(target=function)` makes a thread. `start()` runs it. `join()` waits for it.
- Always use `with lock:`. If you use `lock.acquire()` and forget to release it, other threads wait forever.
- Keep the locked part **small**. While a thread holds the lock, the others wait.

> A **deadlock** happens when two threads each hold a lock that the other one needs, and both wait forever. Avoid it by using one lock when you can, and by taking locks in the same order everywhere.

A class can hold its own lock, so that its users do not have to think about it:

```python
class SafeTotal:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def add(self, n):
        with self._lock:
            self._value += n

    @property
    def value(self):
        return self._value
```

## A queue to share work

`queue.Queue` is a **thread-safe** line of items. It does its own locking. One group of threads **puts** work in, and another group **takes** work out. This is called the **producer / consumer** pattern.

To tell a worker "no more work", put a special end marker in the queue. Often it is `None`, one for each worker:

```python
import queue
import threading

jobs = queue.Queue()
results = []

def worker():
    while True:
        item = jobs.get()             # waits until an item is there
        if item is None:              # the end marker
            break
        results.append(item * 10)

threads = [threading.Thread(target=worker) for _ in range(2)]
for t in threads:
    t.start()

for n in [1, 2, 3, 4]:
    jobs.put(n)
for _ in threads:
    jobs.put(None)                    # one end marker per worker
for t in threads:
    t.join()

print(sorted(results))    # -> [10, 20, 30, 40]
```

If you need the results in the **same order** as the input, put the position with the item, like `(index, item)`, and write each result to `results[index]`. Different threads write to different positions, so they do not clash.

## How to choose

| Situation | Tool |
|---|---|
| waiting on network or disk, a few dozen tasks | `ThreadPoolExecutor` |
| heavy calculation on many cores | `ProcessPoolExecutor` |
| thousands of connections, lots of waiting | `asyncio` (next lesson) |
| one slow thing, nothing else to do | no concurrency needed |

## A little deeper (optional)

- **Why does the GIL exist?** It makes memory management in CPython simple and safe (reference counting, lesson 18). The price is that Python threads cannot run Python code in parallel.
- **The GIL is not a lock for your data.** It can switch threads in the middle of `counter += 1`. You still need your own locks.
- **Libraries.** Heavy number work (NumPy, and so on) runs in C and often lets go of the GIL, so threads can help there too.
- **`multiprocessing`.** The lower-level module under `ProcessPoolExecutor`. Prefer the executor unless you need more control.

## Common mistakes

- Using threads to speed up CPU-bound work. It does not help.
- Changing shared data from many threads with no lock.
- Forgetting to `join()` threads (or to use a `with` pool) and ending the program too early.
- Sending a lambda to a `ProcessPoolExecutor`.
- Leaving out `if __name__ == "__main__":` when using processes.
- Opening thousands of threads. Use a pool with a limit.

## Interview corner

- **Q: What is the GIL?** A lock in CPython that lets only one thread run Python code at a time. It means threads do not speed up CPU-bound work, but they still help with I/O-bound work.
- **Q: Threads, processes or asyncio?** Threads for I/O-bound work with moderate numbers. Processes for CPU-bound work. `asyncio` for a very large number of I/O tasks.
- **Q: What is a race condition?** The result depends on the order in which threads run, because they change shared data without protection. Fix it with a lock or a queue.
- **Q: What is the difference between `map` and `as_completed`?** `map` gives results in input order. `as_completed` gives each future as soon as it is done.

## Summary

- I/O-bound means waiting, CPU-bound means calculating. Pick the tool by that.
- The GIL lets one thread run Python code at a time. Threads help with I/O, processes help with CPU work.
- `ThreadPoolExecutor` and `ProcessPoolExecutor`: `map` (in order), `submit` and `future.result()`, `as_completed`.
- Shared data changed by many threads needs a `Lock` (`with lock:`). A `queue.Queue` shares work safely.
- Errors in a job show up when you call `result()`.

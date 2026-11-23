# 14. Concurrency: threads, processes and the GIL

A program that does one thing at a time wastes time whenever it waits: for a network reply, a disk, a database. **Concurrency** means making progress on several jobs in the same period. This chapter gives you the map of Python's three tools, and the rule for choosing. Chapter 15 then goes deep on the one used most in modern backends: `asyncio`.

## Two kinds of slow

Everything starts with one question: **why is my code slow?**

| Kind | Meaning | Example |
| --- | --- | --- |
| **I/O-bound** | mostly **waiting** for the outside world | calling an API, reading files, a database query |
| **CPU-bound** | mostly **calculating** | resizing images, heavy maths, parsing a huge file |

Think of a cook. If the cook waits for water to boil, the cook can chop vegetables meanwhile (waiting work: do something else). If the cook is chopping, the cook is busy, and the only way to go faster is to add more cooks (calculating work: more workers). The two problems need different fixes.

## The three tools

@@ grid 3 | Figure 14.1: the three tools and when to use them.
Threads|one process;many threads;good for I/O waiting|blue
Processes|many processes;each its own Python;good for CPU work|green
asyncio|one thread;tasks take turns at every await;best for lots of I/O|yellow
@@ end

## The GIL, in plain words

CPython (the normal Python) has a rule called the **GIL**, the Global Interpreter Lock. It says: **only one thread may run Python code at any moment**. Imagine a kitchen with many cooks but only one knife; only the cook holding the knife can chop.

Consequences:

- Threads **cannot** speed up CPU-heavy Python code, since only one runs at a time.
- Threads **do** help with waiting, because a thread that waits for I/O lets go of the knife.
- Separate **processes** each have their own interpreter and their own GIL, so they truly run in parallel.

(Recent Python versions have an optional "free-threaded" build without the GIL. Normal installs still have it, so learn the rule above.)

## Threads

```python
import threading, time

def work(n):
    time.sleep(0.2)          # pretend: waiting on the network
    return n

threads = [threading.Thread(target=work, args=(i,)) for i in range(5)]
start = time.perf_counter()
for t in threads:
    t.start()
for t in threads:
    t.join()
print(round(time.perf_counter() - start, 1))
# -> 0.2
```

Five jobs of 0.2 s took 0.2 s in total, not 1.0 s, because all five were *waiting* at once. `start()` begins a thread and `join()` waits for it to finish.

The easier modern way is a **pool** from `concurrent.futures`:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(3) as pool:
    print(list(pool.map(work, [1, 2, 3])))
# -> [1, 2, 3]
```

`pool.map` runs the function for each item on a pool of threads and gives results in order.

### The danger: shared data and locks

Threads share memory. If two threads change the same variable, the result can be wrong (a **race condition**), because `count += 1` is really three steps (read, add, write) and another thread can slip in between.

```python
lock = threading.Lock()
count = 0

def add_many():
    global count
    for _ in range(100000):
        with lock:
            count += 1
```

A **lock** lets only one thread into the `with lock:` block at a time. The result is then always correct: 4 threads gives `400000`. Races are random: the unlocked version may even look correct on your machine for days, then fail in production. That is what makes them dangerous. Prefer designs that share nothing.

## Processes

For CPU-bound work, use processes. Each has its own memory and its own GIL.

```python
from concurrent.futures import ProcessPoolExecutor

def cpu(n):
    return sum(i * i for i in range(n))

if __name__ == "__main__":
    with ProcessPoolExecutor(4) as pool:
        print(list(pool.map(cpu, [8_000_000] * 4)))
```

Measured on one machine, four jobs of this size took **0.82 s** one after another, **0.82 s** with 4 threads (no gain, the GIL), and **0.37 s** with 4 processes. Your numbers will differ, but the pattern will not.

The `if __name__ == "__main__":` guard (chapter 6) is **required** for processes on some systems, because each new process imports your file again.

The costs: starting a process is slower than a thread, and data sent between processes must be copied (it is "pickled"), so sending huge objects around is slow.

## Choosing

@@ grid 2 | Figure 14.2: how to choose.
Mostly waiting (I/O)|network, database, files;use asyncio for many tasks;or threads if the library blocks|blue
Mostly calculating (CPU)|heavy maths, images, big data;use processes;or move it to a worker queue|yellow
@@ end

In backends: use `asyncio` for lots of web and database calls, a thread (or `run_in_threadpool`) for a blocking library, and a **separate worker process or queue** for heavy CPU jobs. AI note: the model itself usually runs on a GPU or somewhere else, so from your Python code, an LLM call is a **waiting** job, perfect for `asyncio`.

::: {.box .checkpoint}
**Checkpoint:** you can say what I/O-bound and CPU-bound mean, what the GIL stops, and which tool you pick for 100 API calls, and for resizing 100 images.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using threads to speed up calculations (the GIL prevents it).
- Changing shared data from threads without a lock.
- Creating thousands of threads. Use a pool.
- Forgetting `if __name__ == "__main__":` with processes.
- Sending huge objects between processes.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: What is the GIL?** A lock in CPython that lets only one thread run Python bytecode at a time. It makes threads useless for CPU-bound Python code, but they still help with I/O.

**Q: Threads vs processes vs asyncio?** Threads share memory and suit blocking I/O. Processes use separate memory and cores and suit CPU work. `asyncio` uses one thread with cooperative tasks and suits many concurrent I/O operations.

**Q: Concurrency vs parallelism?** Concurrency is dealing with many things in overlapping time. Parallelism is running at the same instant on many cores.

**Q: What is a race condition?** A bug where the result depends on the unpredictable order in which threads touch shared data.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Run 5 jobs that each `sleep(0.5)` one after another, then with a thread pool. Compare.
2. Make a CPU-heavy function, time it sequentially, with threads and with processes.
3. Write the counter with and without a lock, and run 4 threads. Is the unlocked one always wrong on your machine?
4. List three tasks from your own projects and mark each I/O-bound or CPU-bound.
5. **Think:** why does a process pool need the `__main__` guard?
:::

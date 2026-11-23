---
title: Level 3 interview questions
summary: The Level 3 topics as interviewers ask them - concurrency, asyncio, packaging, testing and performance - with follow-ups, short answers and tools for the coding exercises.
plan_ids: [PY-08, PY-09, PY-10, PY-11]
---

This is interview practice for Level 3. Use it the same way as before:

1. Read a question and **answer it out loud first**.
2. Then read the model answer.
3. Try the follow-ups. Interviewers usually ask two or three.

## 1. Threads, processes and the GIL (lesson 30)

**Q: What is the GIL, and what does it mean for your code?**

**A:** The GIL lets only one thread run Python code at a time in normal CPython. So threads do **not** speed up CPU-bound work, but they do help I/O-bound work, because a waiting thread lets go of the GIL. For CPU-bound work, use processes.

What is printed, and is it always the same?

```python
import threading

count = 0

def work():
    global count
    for _ in range(100_000):
        count += 1

threads = [threading.Thread(target=work) for _ in range(4)]
for t in threads: t.start()
for t in threads: t.join()
print(count)
```

**A:** It can print less than `400000`, and the number can change between runs. `count += 1` is read, add, write. Threads can mix these steps, and an update is lost (a **race condition**). Fix it with a `threading.Lock` and `with lock:`.

Follow-ups:

- *Does the GIL protect your data?* No. It can switch threads between the steps of `count += 1`. You still need locks.
- *`ThreadPoolExecutor.map` or `as_completed`?* `map` gives results in input order. `as_completed` gives each one as soon as it is ready.
- *What is a deadlock?* Two threads each hold a lock the other one needs, and both wait forever. Take locks in the same order everywhere.

## 2. asyncio (lesson 31)

**Q: Threads or asyncio?**

**A:** Both are for waiting work. Threads are simple (normal functions) and fine for dozens of tasks. asyncio handles thousands of tasks on one thread, but everything on the path must be `async`, and a task only switches at an `await`.

What happens here?

```python
async def main():
    await asyncio.sleep(1)
    time.sleep(5)
```

**A:** `time.sleep(5)` blocks the whole event loop for 5 seconds, so every other task freezes. Use `await asyncio.sleep`, or `await asyncio.to_thread(...)` for blocking code.

Follow-ups:

- *How do you run 500 requests with at most 10 at once?* An `asyncio.Semaphore(10)` with `async with`, and `gather`.
- *What does `gather(..., return_exceptions=True)` change?* Errors come back in the result list, and the other results are kept.
- *How do you stop waiting after 2 seconds?* `async with asyncio.timeout(2):`, and catch `TimeoutError`.
- *How do you stream an AI answer?* An async generator read with `async for`, for example inside a FastAPI `StreamingResponse`.

## 3. Packaging with uv (lesson 32)

**Q: What is the difference between `pyproject.toml` and `uv.lock`?**

**A:** `pyproject.toml` says which versions you **accept** (`fastapi>=0.110`). `uv.lock` records the **exact** versions that were chosen, so every install is the same. Commit both. Do not commit `.venv`.

Follow-ups:

- *Why a virtual environment?* Each project gets its own libraries, so versions do not clash.
- *What does `>=1.4,<2.0` mean?* New features and fixes are fine, but a major version (which can break things) is not.
- *What is `[project.scripts]`?* It turns `module:function` into a command, like `taskflow = "taskflow.cli:main"`.
- *Why is `"1.10" > "1.9"` false as text?* Text compares character by character. Compare versions as tuples of ints.

## 4. Testing (lesson 33)

**Q: How do you make code easy to test?**

**A:** Pass the things it depends on (clock, database, mailer, HTTP client) in from outside, instead of creating them inside. In tests, give it a fake. Then tests are fast and repeatable, with no real network, no waiting and no real email.

Follow-ups:

- *What is a fixture?* A function that prepares data for tests. A test asks for it by name. With `yield` it can clean up afterwards.
- *Fake or mock?* A fake is a simple working stand-in. A mock records the calls so you can check them.
- *How do you test a function that reads an environment variable?* `monkeypatch.setenv`.
- *How do you test that an error is raised?* `with pytest.raises(ValueError):`.
- *What makes a test bad?* It depends on another test, uses the real network, has no `assert`, or tests many things at once.

## 5. Performance (lesson 34)

**Q: A function is slow. What do you do?**

**A:** Measure first, with a profiler like `cProfile`, to find the function that takes the most time. Fix that one (usually the data structure or the algorithm), then measure again.

Follow-ups:

- *Why is `x in a_set` faster than `x in a_list`?* A set uses hashing, so it takes O(1). A list scans, so it takes O(n).
- *What is wrong with `s += piece` in a loop?* It copies the whole string each time. Collect pieces and use `"".join`.
- *How do you handle a 20 GB file?* Read it line by line with a generator, and keep only counters.
- *When would you NOT use `lru_cache`?* For functions with side effects, or ones that depend on changing data, or when the cache could grow without a limit.

## 6. Quick answers

| Question | Short answer |
|---|---|
| CPU-bound or I/O-bound | calculating all the time, or waiting for the outside |
| Which pool for CPU work | `ProcessPoolExecutor` (each process has its own GIL) |
| Why `with lock:` | it always releases the lock, even after an error |
| `await` outside `async def` | not allowed (SyntaxError) |
| Forgetting `await` | you get a coroutine object that never ran |
| `gather` order | the order you gave, not the finish order |
| Dev dependency | a library needed only while developing, like pytest |
| `parametrize` | run one test with many inputs |
| Big-O of `x in set` | O(1) on average |
| `sorted` | O(n log n) |

## Tools for the three coding exercises

These small examples show the tools. They are not the answers.

### Retry with a pause you can fake (exercise 1)

An `async` function can `await` another function that was passed in. Passing in the sleep function lets a test skip the real waiting:

```python
import asyncio

async def run_twice(job, sleep=asyncio.sleep):
    results = []
    for round_number in range(2):
        results.append(await job(round_number))
        await sleep(0.5)               # in a test: pass a fake that does nothing
    return results

async def fake_sleep(seconds):
    pass

async def job(n):
    return n * 10

print(asyncio.run(run_twice(job, sleep=fake_sleep)))     # -> [0, 10]
```

Think about it: which errors should be retried, which should not, and when must the last error be raised again? (Lesson 21 has the same idea for normal code.)

### Do something only once, even with many threads (exercise 2)

When two threads ask for the same thing at the same moment, both may think "it is not there yet" and both do the work. A lock around the **check and the work together** stops this:

```python
import threading

lock = threading.Lock()
data = {}

def get_or_make(key, make):
    with lock:
        if key not in data:
            data[key] = make(key)
        return data[key]
```

The first thread does the work. The others wait, and then find the value. (A real solution may want a separate lock for each key, so slow work for one key does not block the others. That is an extra challenge.)

### Streaming counts (exercise 3)

A `Counter` can be fed one item at a time, so memory depends on the number of **different** keys, not on the number of lines:

```python
from collections import Counter

counts = Counter()
for word in (w for w in "a b a c a b".split()):
    counts[word] += 1

print(counts.most_common(2))     # -> [('a', 3), ('b', 2)]
```

To break ties in a fixed way, sort with a tuple key (lesson 25): by count from big to small, and then by name from A to Z.

## How to practise

1. Do the three coding exercises **under time pressure** (20 to 25 minutes each).
2. Say the complexity out loud **before** you run the tests.
3. Ask Claude: *"Act as an interviewer. Ask me 5 follow-up questions on asyncio, one at a time, and grade my answers."*

## Summary

- Know the split: CPU-bound needs processes, I/O-bound needs threads or asyncio.
- Know the traps: the race in `count += 1`, blocking calls in async code, forgetting `await`, comparing versions as text, and `x in list` in a loop.
- Know the habits: measure before you optimise, inject dependencies, use fakes, and commit `uv.lock`.
- Give the reason as well as the answer.

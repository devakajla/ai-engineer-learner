---
title: Performance & profiling
summary: Find out why code is slow by measuring it, then fix it with better data structures, caching, lazy work and early exits.
plan_ids: [PY-11]
---

Fast code is nice. **Correct, clear** code is more important. Make code fast only when it is **too slow**, and only after you **measure** where the time goes. Programmers are often wrong about which line is slow.

The rule of this lesson:

1. **Measure** first.
2. Fix the **biggest** problem.
3. Measure **again** to see that it helped.

## Measure with `timeit`

`timeit` runs a small piece of code many times and tells you the total time in seconds.

```python
import timeit

seconds = timeit.timeit("sum(range(100))", number=10_000)
print(seconds < 5)        # -> True      the exact number changes on every computer
```

`timeit.repeat(..., repeat=3)` gives a list of times, one per round. Use the **smallest** one. Other programs on your computer can only make a run slower, never faster, so the smallest time is the most honest.

To time a single call yourself, use `time.perf_counter()` (lesson 23):

```python
import time

start = time.perf_counter()
result = sum(range(1_000_000))
elapsed = time.perf_counter() - start
```

### A step-by-step example: a helper that measures

1. Take the function and how many rounds to run.
2. For each round: read the timer, call the function, read the timer, store the difference.
3. Return the smallest difference.

```python
import time

def best_time(func, rounds=3, timer=time.perf_counter):
    times = []
    for _ in range(rounds):
        start = timer()
        func()
        times.append(timer() - start)
    return min(times)

print(best_time(lambda: sum(range(1000))) < 1)    # -> True
```

The `timer` is a parameter, so a test can give a fake one (lesson 33).

## Find the slow part with a profiler

When a big program is slow, you do not know **which function** to fix. A **profiler** counts how long each function takes. Python has `cProfile`:

```python
import cProfile
import pstats

def slow_part():
    return sum(i * i for i in range(200_000))

def fast_part():
    return 1 + 1

def main():
    slow_part()
    fast_part()

profiler = cProfile.Profile()
profiler.enable()
main()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats("cumulative").print_stats(5)    # the 5 slowest, including the functions they call
```

From the terminal you can also run `python -m cProfile -s cumulative myscript.py`.

Look at two columns in the output:

- `ncalls`: how many times it was called.
- `cumtime`: total time in this function, including the functions it calls.

A function with a large `cumtime` is where to look first.

## Big-O: how time grows

**Big-O** describes how the time **grows when the input grows**. You will see it in every interview.

| Name | Written | Example | 10× more data means |
|---|---|---|---|
| constant | O(1) | `d[key]`, `x in a_set`, `list.append` | same time |
| logarithmic | O(log n) | binary search | a little more |
| linear | O(n) | `x in a_list`, `sum(list)` | 10× the time |
| n log n | O(n log n) | `sorted(list)` | a bit over 10× |
| quadratic | O(n²) | a loop inside a loop | 100× the time |

Quadratic code feels fine with 100 items and is unusable with 100,000.

## The most common fix: the right data structure

Looking for a value in a **list** checks the items one by one: O(n). Looking in a **set** or a **dict** is O(1), because of hashing (lesson 18).

```python
allowed = ["ana", "bo", "cy"] * 10_000       # a long list
names = ["bo", "zed"]

slow = [n for n in names if n in allowed]            # scans the list for every name

allowed_set = set(allowed)                           # build the set once
fast = [n for n in names if n in allowed_set]        # each check is O(1)
print(fast)     # -> ['bo']
```

A step-by-step example: find the items that are in **both** of two lists.

```python
a = [5, 3, 8, 1]
b = [8, 2, 5, 9]
```

1. The slow way: for each item in `a`, check `item in b`. That is a loop inside a loop: O(n × m).
2. The fast way: turn one list into a set (O(m)), then check each item of the other list (O(n) checks, each O(1)).
3. Or use the set operation `&`, which gives the items in both: `set(a) & set(b)`.

```python
print(sorted(set(a) & set(b)))      # -> [5, 8]
```

Other good choices:

| Need | Use |
|---|---|
| "is it in there?" many times | `set` or `dict` |
| take from the left end | `deque`, not `list.pop(0)` |
| the biggest few items | `heapq.nlargest(3, items)` |
| count things | `Counter` |
| a sorted list you search often | `bisect` |

```python
import heapq

print(heapq.nlargest(2, [5, 1, 9, 3]))     # -> [9, 5]
```

## Build strings with `join`

Strings cannot change (lesson 4). `text += piece` in a loop makes a **new** string every time, copying everything. Collect the pieces in a list, and `join` once:

```python
pieces = []
for i in range(5):
    pieces.append(str(i))
print(",".join(pieces))      # -> 0,1,2,3,4
```

## Do not repeat work

Move work **out of the loop** if it gives the same answer each time:

```python
# slow: len(data) and the lookup are repeated 100,000 times
for i in range(100_000):
    total += len(data) * rate_for("EUR")

# better: do it once
size = len(data)
rate = rate_for("EUR")
for i in range(100_000):
    total += size * rate
```

If the **same call** is made with the **same arguments** again and again, remember the answer. This is **caching** (lesson 23's `lru_cache`). It is a big win for calculations that call themselves, like the number of paths in a grid:

```python
from functools import cache

@cache
def paths(rows, cols):
    if rows == 1 or cols == 1:
        return 1
    return paths(rows - 1, cols) + paths(rows, cols - 1)

print(paths(3, 3))        # -> 6
print(paths(30, 30))      # -> 30067266499541040    instant. Without the cache, it would take years.
```

Without `@cache`, the same `paths(2, 2)` is worked out again and again, and the work **doubles** at every level. With the cache, each pair is worked out **once**.

> Caching trades **memory** for **time**. Only cache pure functions (lesson 23), and watch the size.

## Be lazy, and stop early

Do not do work you do not need.

- A **generator** (lesson 22) makes one item at a time, so memory stays small.
- `any(...)` and `all(...)` stop at the first answer.
- A loop can `return` or `break` as soon as it knows the answer.

```python
def first_negative(numbers):
    for n in numbers:
        if n < 0:
            return n          # stop here, do not look at the rest
    return None

print(first_negative([4, 7, -2, 9, -5]))     # -> -2
```

If `numbers` is a generator with a million items, this reads only three of them.

## Memory

Speed is not everything. A program can also use too much **memory**.

```python
import sys

print(sys.getsizeof(list(range(1000))) > sys.getsizeof(range(1000)))    # -> True
```

A list of a million items is big. A `range` or a generator is tiny, because it does not hold the items. `sys.getsizeof(x)` shows the size of one object in bytes (not the objects inside it). The `tracemalloc` module shows where memory is used.

Tips: use generators for big data, read files line by line (lesson 22), and use tuples instead of lists for millions of small records.

## When Python is not fast enough

- Use the right **algorithm** first. It beats everything else.
- Use libraries written in C (NumPy for numbers, Pydantic's Rust core for validation).
- For CPU-bound work, use processes (lesson 30).
- For waiting, use threads or `asyncio` (lessons 30 and 31).
- Only then think about other tools (for example Cython or Rust extensions).

## A little deeper (optional)

- **Why is a list `in` slow and a set `in` fast?** A set stores items by their hash, so it jumps to the right place. A list has no such index.
- **Amortised O(1).** `list.append` is sometimes slow (when the list must grow), but on average it is O(1).
- **Local names are faster.** Inside a hot loop, a local variable is a little faster to look up than a global one. This rarely matters. Fix the algorithm first.
- **Sampling profilers** such as `py-spy` can look at a running program without changing it.
- **Benchmarks lie** if the test data is too small or too different from real data.

## Common mistakes

- Optimising without measuring.
- Checking `x in some_list` inside a loop.
- Building a big string with `+=` in a loop.
- Making a big list when a generator is enough.
- Caching a function that has side effects, or caching with no limit.
- Timing once, and trusting the number. Repeat, and use the smallest.

## Interview corner

- **Q: How do you find out why a program is slow?** Measure. Use a profiler like `cProfile` to find the functions with the most time, then fix the biggest one, and measure again.
- **Q: Why is `x in my_set` faster than `x in my_list`?** A set uses hashing, so a lookup takes O(1). A list checks items one by one, which is O(n).
- **Q: What does O(n²) mean, and how do you avoid it?** The time grows with the square of the input, usually from a loop inside a loop. Use a set or dict for the inner lookup.
- **Q: When is caching a bad idea?** When the function has side effects, depends on changing data like the time, or when the cache could grow without a limit.
- **Q: How do you keep memory low when handling a big file?** Read it line by line with a generator, and do not load it all into a list.

## Summary

- Measure first: `timeit`, `time.perf_counter`, and `cProfile` for the slow function.
- Big-O says how time grows. Avoid loops inside loops over big data.
- Sets and dicts are O(1) for lookups. Use `join` for strings, `deque` for queues, `heapq` for the biggest few.
- Do not repeat work: move it out of the loop, or cache it.
- Be lazy: generators, `any` / `all`, and stop early.
- Watch memory as well as time.

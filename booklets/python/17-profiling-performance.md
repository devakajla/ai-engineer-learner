# 17. Profiling and performance

"My code is slow" is a feeling. **Profiling** turns it into a fact: *which* part is slow, and by how much. The golden rule: **measure first, then change.** Programmers are famously bad at guessing where the time goes.

## Step 1: time a piece of code

`time.perf_counter()` gives a precise clock. For a tiny snippet use `timeit`, which repeats it many times and averages the noise.

```python
import timeit

seconds = timeit.timeit("[i * i for i in range(1000)]", number=1000)
print(seconds > 0)
# -> True
```

`number=1000` runs the code a thousand times. Compare two versions with the same `number` to see which is faster.

## Step 2: find the slow part with a profiler

`cProfile` records how long **every function** took and how often it was called.

```python
import cProfile, pstats, io

def slow():
    return sum(i for i in range(100000))

profiler = cProfile.Profile()
profiler.enable()
slow()
profiler.disable()

out = io.StringIO()
pstats.Stats(profiler, stream=out).sort_stats("cumulative").print_stats(3)
print(out.getvalue())
```

You can also run a whole script: `python -m cProfile -s cumulative main.py`. Read the table like this: `ncalls` is how many times a function was called, `tottime` is time spent in the function itself, and `cumtime` is time including everything it called. Sort by `cumulative` to find the biggest area, and then look at what is inside it.

## Step 3: memory

`tracemalloc` shows how much memory your code allocates:

```python
import tracemalloc

tracemalloc.start()
data = [i for i in range(100000)]
current, peak = tracemalloc.get_traced_memory()
print(peak > 0)
# -> True
```

A generator (chapter 10) uses far less memory than a list for the same values.

## The big wins (most slowness is one of these)

### 1. A wrong data structure

Checking `x in my_list` scans item by item. Checking `x in my_set` jumps straight to it. Measured with 100,000 items and 1000 lookups of the last item:

```python
L = list(range(100000))
S = set(L)
print(timeit.timeit(lambda: 99999 in L, number=1000))
# -> 0.486
print(timeit.timeit(lambda: 99999 in S, number=1000))
# -> 0.00002
```

The set was about **20,000 times faster**. This one change fixes a lot of real programs. Remember from chapter 4: use a set or dict for "is it in there?".

### 2. Doing the same work again and again

Cache results of repeated, pure calculations with `functools.lru_cache` (chapter 11). Move a calculation that does not change **out** of the loop.

### 3. Building strings with `+=` in a loop

```python
text = ""
for i in range(50000):
    text += "x"          # copies the growing string again and again

text2 = "".join("x" for _ in range(50000))   # builds it once
```

On one machine the first took 0.069 s and the `join` took 0.002 s. Collect pieces in a list and `join` them at the end.

### 4. The N+1 problem

The most common slowness in backends: **one** query to get a list, then **one more query per item**. 100 items means 101 database calls. Fix by fetching everything in one query (a join, or `IN (...)`), or by loading related rows in a batch. In FastAPI with SQLAlchemy the tools are `selectinload` and `joinedload`.

### 5. Waiting one at a time

Ten API calls of 0.5 s each take 5 s one after another, but about 0.5 s with `asyncio.gather` (chapter 15).

## The attitude

@@ vflow | Figure 17.1: the performance loop.
Measure|time it; profile it|blue -> Find the biggest cost|the one line or call that dominates|yellow -> Change one thing|a better structure, cache, batch|green -> Measure again|did it really improve?|blue
@@ end

Do not optimise code that is not a problem. Readable code that is fast enough beats clever code that is faster than needed. And always keep the tests green while you speed things up.

::: {.box .checkpoint}
**Checkpoint:** you can name the five big wins, and you profile before you change anything.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Optimising by guessing, without measuring.
- Timing once and trusting it (use `timeit` and repeat).
- A list for lookups instead of a set or dict.
- Calling a database or API inside a loop.
- Making code unreadable for a tiny gain.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: How do you find why code is slow?** Profile it (`cProfile`), look at where the time goes, fix the biggest part, and measure again.

**Q: Why is `x in set` faster than `x in list`?** A set uses hashing to jump to the item. A list scans through it.

**Q: What is the N+1 query problem?** One query for a list and then one per item. Fix with a join or batch loading.

**Q: Why is `+=` on strings in a loop slow?** Strings are immutable, so each `+=` makes a new copy. Use `"".join(parts)`.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Compare `x in list` and `x in set` for 10,000 items using `timeit`.
2. Profile a function that calls a slow helper many times. Which line of the report shows it?
3. Fix a loop that builds a string with `+=` using `join`, and time both.
4. Speed up a recursive Fibonacci with `lru_cache` and time it.
5. Find the N+1 pattern in this idea: "for each user, call `get_orders(user_id)`". How would you fetch in one call?
6. **Think:** why is it risky to optimise before profiling?
:::

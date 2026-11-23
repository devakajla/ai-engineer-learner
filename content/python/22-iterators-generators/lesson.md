---
title: Iterators & generators
summary: How a for loop really works, and how generators handle huge or endless data one item at a time, using very little memory.
plan_ids: [PY-02]
---

Generators are everywhere in backend and AI work: reading a big file line by line, going through pages of an API, or **streaming AI answers word by word** to a user. This lesson explains how they work under the hood.

## How `for` really works

This loop:

```python
for x in [10, 20]:
    print(x)
```

is really doing this:

```python
it = iter([10, 20])        # ask the list for an iterator
while True:
    try:
        x = next(it)       # ask the iterator for the next item
    except StopIteration:  # the iterator says "no more items"
        break
    print(x)
```

Two words to know:

- An **iterable** is something you can loop over (a list, a string, a dict, a file). `iter(thing)` gives you an iterator from it.
- An **iterator** gives out items one at a time with `next()`. When there are no more, it raises `StopIteration`.

An iterator can be used **only once**. When it is used up, it stays empty:

```python
it = iter([1, 2])
print(list(it))   # -> [1, 2]
print(list(it))   # -> []     used up!
```

## Writing an iterator class

To make your own iterator, write a class with two methods: `__iter__` (returns itself) and `__next__` (gives the next item, or raises `StopIteration` at the end).

```python
class UpTo:
    def __init__(self, stop):
        self.current = 0
        self.stop = stop

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        self.current += 1
        return self.current

print(list(UpTo(3)))    # -> [1, 2, 3]
```

Notice that the object keeps its place in `self.current`. That is how it knows what to give next. It also means that it is used up after one pass.

That is a lot of code for a simple idea. **Generators** do the same in a few lines.

## Generator functions and `yield`

A function that contains `yield` is a **generator function**. When you call it, it does **not** run. It gives you a generator (a kind of iterator). The body runs **lazily**: it runs until a `yield`, hands out the value, and pauses. The next `next()` continues from that spot.

```python
def up_to(stop):
    n = 1
    while n <= stop:
        yield n
        n += 1

g = up_to(3)      # nothing runs yet!
print(next(g))    # -> 1   runs until the first yield
print(next(g))    # -> 2   continues right after the yield
print(list(g))    # -> [3]
```

The variables keep their values while the function is paused. Because nothing runs at the call, this prints in a surprising order:

```python
def gen():
    print("start")
    yield 1

g = gen()
print("created")    # -> created
next(g)             # -> start
```

## Why lazy is useful

A list holds **all** its items in memory. A generator makes **one** item at a time.

```python
def read_lines(path):
    with open(path) as f:
        for line in f:                 # a file is a lazy iterator too
            yield line.rstrip("\n")

for line in read_lines("10GB.log"):    # uses almost no memory
    ...
```

A list of all lines of a 10 GB file would crash the program. The generator uses only a few kilobytes.

## Generator expressions

A generator expression looks like a list comprehension, but with round brackets. It is lazy:

```python
squares = [x * x for x in range(10**7)]   # builds 10 million numbers in memory
squares = (x * x for x in range(10**7))   # lazy: nothing is computed yet
total = sum(x * x for x in range(10**7))  # the extra () are not needed inside sum(...)
```

A generator is used up after one pass, just like any iterator:

```python
nums = (x * 2 for x in [1, 2, 3])
print(sum(nums))    # -> 12
print(sum(nums))    # -> 0     used up
```

Lazy things you already know: files, `range`, `enumerate`, `zip` and `map`. A list or a tuple is **not** lazy.

## Pipelines: chain generators together

Each step takes items from the step before it, one at a time. It is like a pipe in the terminal, and it uses constant memory.

A step-by-step example. Each line of a log looks like `"ERROR disk full"`. We want the messages of the first two errors.

1. `parse` turns each line into a dict, skipping blank lines.
2. `only_errors` keeps only the records with level `ERROR`.
3. `islice` takes just the first 2 items. After that, nothing more is read from the file.

```python
from itertools import islice

def parse(lines):
    for line in lines:
        if not line.strip():
            continue                          # skip blank lines
        level, msg = line.split(" ", 1)       # split at most 1 time
        yield {"level": level, "msg": msg}

def only_errors(records):
    return (r for r in records if r["level"] == "ERROR")

lines = ["INFO started", "ERROR disk full", "", "ERROR network down", "ERROR other"]
first_two = list(islice(only_errors(parse(lines)), 2))
print([r["msg"] for r in first_two])    # -> ['disk full', 'network down']
```

`split(" ", 1)` splits only at the first space, so the message keeps its own spaces.

Laziness means work stops as soon as the one asking stops asking.

## `islice`: take part of a lazy thing

A generator has no `len()` and cannot be sliced with `[:5]`. To take a limited number of items, use `itertools.islice`:

```python
from itertools import islice

g = up_to(100)
print(list(islice(g, 3)))    # -> [1, 2, 3]
print(list(islice(g, 3)))    # -> [4, 5, 6]   it continues where it stopped
```

`islice(it, n)` takes up to `n` **next** items. If the iterator has fewer left, it gives what is left. When nothing is left, it gives an empty result. That is a handy tool for cutting any iterable into batches.

To turn any iterable (a list, a generator, ...) into an iterator that moves forward, use `iter(...)`:

```python
it = iter([10, 20, 30, 40, 50])
print(list(islice(it, 2)))    # -> [10, 20]
print(list(islice(it, 2)))    # -> [30, 40]
print(list(islice(it, 2)))    # -> [50]
print(list(islice(it, 2)))    # -> []
```

## `yield from`

`yield from` hands out every item of another iterable, one after another:

```python
def flatten(list_of_lists):
    for inner in list_of_lists:
        yield from inner

print(list(flatten([[1, 2], [3]])))    # -> [1, 2, 3]
```

## Endless generators

A generator can run forever, because it only makes a value when asked:

```python
def ids(start=1):
    n = start
    while True:
        yield n
        n += 1

gen = ids()
print(next(gen), next(gen))    # -> 1 2
```

Never call `list()` on an endless generator. It will never finish. Use `islice` to take a limited number.

## Errors in a generator come late

Because a generator body does not run until the first `next()`, an error inside it (like a bad argument) shows up late, when you start looping, and not when you call the function. To fail early, **check the arguments in a normal function** and then return the generator:

```python
def up_to_checked(stop):
    if stop < 1:
        raise ValueError("stop must be at least 1")    # runs right at the call
    return _up_to(stop)

def _up_to(stop):
    n = 1
    while n <= stop:
        yield n
        n += 1
```

Here the `ValueError` is raised as soon as you call `up_to_checked(0)`, even before you loop.

## A little deeper (optional)

**A real example.** Going through the pages of an API:

```python
def fetch_all(client, url):
    page = 1
    while True:
        data = client.get(url, params={"page": page}).json()
        if not data["items"]:
            return                    # ends the generator
        yield from data["items"]
        page += 1
```

The caller just writes `for task in fetch_all(...)`. The pages are hidden, and only one page is in memory.

**Cleanup.** If the loop stops early, Python closes the generator. Its `with` blocks and `finally` blocks still run. So `with open(...)` inside a generator is safe.

## Common mistakes

- Looping over a used-up iterator a second time and getting nothing.
- Calling `len()` on a generator. It does not know its length.
- Calling `list()` on a huge or endless generator.
- Expecting the code before the first `yield` to run when you call the generator function. It runs on the first `next`.

## Interview corner

- **Q: What is the difference between an iterable and an iterator?** An iterable gives you an iterator when you call `iter()` on it. An iterator gives items with `next()` and can be used only once.
- **Q: What does `yield` do?** It turns the function into a generator. It pauses the function and hands out a value. The next `next()` continues from that spot.
- **Q: Why use generators?** They are lazy: constant memory for big or endless data, they can stop early, and they chain into pipelines.
- **Q: How would you stream an AI answer through FastAPI?** Return a `StreamingResponse` wrapped around a generator that yields the words as they arrive.

## Summary

- `for` calls `iter()` and then `next()` until `StopIteration`.
- Generator functions (`yield`) and generator expressions `(...)` are lazy and can be used only once.
- Chain generators into pipelines. `yield from` hands out another iterable. `islice` takes a limited number of items.
- Use generators for big files, pages of an API and streaming.

# 10. Iterators and generators

Every `for` loop you have written rests on one idea: **iteration**. This chapter shows how it works, and how to write **generators**: functions that produce values one at a time instead of all at once. Generators are how Python handles huge data, streams and (later) LLM token streams.

## What "iterable" and "iterator" mean

- An **iterable** is anything you can loop over: list, string, dict, file.
- An **iterator** is the object that actually walks through it, giving the **next** item each time you ask.

A `for` loop quietly does two steps: it asks the iterable for an iterator (`iter()`), then calls `next()` again and again until the iterator says it is empty.

```python
it = iter([1, 2])
print(next(it), next(it))
# -> 1 2
next(it)
# -> StopIteration
```

`StopIteration` is the signal "nothing left". The `for` loop catches it for you and stops quietly. An iterator is a **one-way ticket**: once an item is given, it is gone, and you cannot go back.

## Writing an iterator by hand (to see how it works)

```python
class Countdown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

print(list(Countdown(3)))
# -> [3, 2, 1]
```

An iterator needs `__iter__` (return itself) and `__next__` (give the next item or raise `StopIteration`). It works, but it is a lot of code for a simple idea. Generators solve that.

## Generators: iterators made easy

A **generator function** looks like a normal function, but uses `yield` instead of `return`. Each `yield` hands out one value and **pauses** the function, remembering exactly where it was. The next request resumes from that spot.

```python
def count(n):
    i = 1
    while i <= n:
        yield i
        i += 1

gen = count(3)
print(next(gen), list(gen))
# -> 1 [2, 3]
```

Calling `count(3)` does **not** run the body. It returns a generator object. `next(gen)` runs until the first `yield` (giving 1) and pauses. `list(gen)` then pulls the remaining values, 2 and 3. A normal `return` ends a function for good. A `yield` pauses it.

You can see the pausing:

```python
def numbers():
    print("start")
    yield 1
    print("middle")
    yield 2

g = numbers()
print("created")
print(next(g))
print(next(g))
# -> created
# -> start
# -> 1
# -> middle
# -> 2
```

Nothing printed at creation. "start" appeared only when the first value was requested. This is **lazy evaluation**: work happens only when needed.

@@ flow | Figure 10.1: a generator pauses at every yield.
next()|ask for a value|blue -> run to yield|do some work|yellow -> pause + give value|keep local state|green -> next()|resume exactly here|blue
@@ end

## Why generators matter

**1. Memory.** A list of a billion numbers will not fit in memory. A generator holds one number at a time.

```python
import sys
big_list = [i for i in range(10000)]
lazy = (i for i in range(10000))
print(sys.getsizeof(big_list) > sys.getsizeof(lazy))
# -> True
```

**2. Streams of unknown length.** Reading a huge log file line by line, or receiving tokens from an AI model as they are produced, is naturally a generator.

**3. Pipelines.** Chain generators like pipes in a factory: each step takes values from the previous one and hands on its results, and no big list is ever made.

```python
def evens(items):
    for x in items:
        if x % 2 == 0:
            yield x

def squares(items):
    for x in items:
        yield x * x

print(list(squares(evens(range(7)))))
# -> [0, 4, 16, 36]
```

Follow one value: `0` goes through `evens` (kept), then `squares` (0). `1` is dropped by `evens`. `2` is kept and squared to 4, and so on. Each value travels the whole pipeline before the next one starts.

## Useful tools

`yield from other` hands over every value of another iterable:

```python
def inner():
    yield from [1, 2]

print(list(inner()))
# -> [1, 2]
```

The `itertools` module has ready-made lazy tools:

```python
import itertools

print(list(itertools.islice(itertools.count(5), 3)))
# -> [5, 6, 7]
print(list(itertools.chain([1], [2])))
# -> [1, 2]
```

`count(5)` would count forever, but `islice` takes only the first 3. This is only safe because everything is lazy.

## One-shot warning

A generator can be used **once**. After it is exhausted, it gives nothing:

```python
g = (n for n in range(3))
print(list(g), list(g))
# -> [0, 1, 2] []
```

If you need the data twice, turn it into a list first, or create the generator again.

::: {.box .checkpoint}
**Checkpoint:** you can explain what `yield` does, why creating a generator runs no code, and when you would choose a generator over a list.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Using a generator twice and getting nothing the second time.
- Calling `len()` on a generator (it has no length).
- Expecting a generator function to run when you call it.
- Turning a huge generator into a list and losing the memory benefit.
- Using `return value` inside a generator and expecting it as a normal item.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Iterable vs iterator?** An iterable can produce an iterator. An iterator remembers its position and gives items through `next()`.

**Q: What does `yield` do?** Produces a value and pauses the function, keeping its state until the next request.

**Q: Why use generators?** Low memory, lazy work, and the ability to model infinite or streaming data.

**Q: Generator vs list comprehension?** A comprehension builds everything now. A generator makes items on demand.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Write `evens_up_to(n)` as a generator.
2. Write `read_lines(path)` that yields stripped lines one by one.
3. Build a pipeline: numbers, keep multiples of 3, multiply by 10, and take the first 4 with `islice`.
4. Write a generator for the Fibonacci numbers that never stops, and print the first 10.
5. Show that a generator is exhausted after one use.
6. **Think:** how is streaming an AI answer token by token similar to a generator?
:::

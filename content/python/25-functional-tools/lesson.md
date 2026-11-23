---
title: "lambda, itertools, functools"
summary: Handy tools for sorting, searching, grouping and joining data in short, clear lines, using lambda, itertools and functools.
plan_ids: [PY-02, PY-03]
---

A lot of real code does the same few jobs: take a collection, change it, filter it, group it, sort it. Python has built-in tools that do each of these in one clear line. Many are lazy and written in C, so they are fast too.

## `lambda`: a tiny function without a name

A `lambda` is a small function written in one line. It has the form `lambda inputs: result`.

```python
double = lambda x: x * 2
print(double(4))      # -> 8
```

Do not give a lambda a name like this. Use `def` for functions that have a name. The real use of a lambda is a throw-away function that you pass to another function:

```python
words = ["pear", "fig", "banana"]
print(sorted(words, key=lambda w: len(w)))    # -> ['fig', 'pear', 'banana']
```

A lambda can only hold **one expression**. For anything longer, or anything you want to test, use `def`.

## Sorting with `key`

`sorted(items, key=function)` sorts by what the function gives for each item.

```python
users = [{"name": "ana", "age": 31}, {"name": "Dev", "age": 22}, {"name": "bo", "age": 31}]

by_age = sorted(users, key=lambda u: u["age"])
print([u["name"] for u in by_age])         # -> ['Dev', 'ana', 'bo']

print(sorted(["b", "A", "c"], key=str.lower))    # -> ['A', 'b', 'c']   ignore the case
```

`min()` and `max()` take a `key` too:

```python
oldest = max(users, key=lambda u: u["age"])
print(oldest["name"])      # -> ana
```

`max` and `min` also take `default=...` for an empty collection. Without it, an empty collection is a `ValueError`:

```python
print(max([], default=None))     # -> None
```

### Sort by two things, one of them going down

Use a **tuple** as the key. Python compares tuples item by item. To sort a number from big to small, put a **minus** in front of it:

```python
users = [{"name": "ana", "age": 31}, {"name": "Dev", "age": 22}, {"name": "bo", "age": 31}]
result = sorted(users, key=lambda u: (-u["age"], u["name"]))
print([u["name"] for u in result])      # -> ['ana', 'bo', 'Dev']
```

This reads: oldest first, and when the ages are the same, the names from A to Z. (`reverse=True` would also reverse the names, which is not what we want here.)

Good to know:

- `sorted()` gives a **new list** and does not change the old one. `list.sort()` changes the list and returns `None`.
- Python's sort is **stable**: items with equal keys keep their old order.
- `operator.itemgetter("age")` is a faster, shorter replacement for `lambda u: u["age"]`.

## `map` and `filter`

```python
print(list(map(str.upper, ["a", "b"])))     # -> ['A', 'B']
print(list(filter(None, [0, 1, "", "x"])))  # -> [1, 'x']     drops falsy values
```

A comprehension (lesson 12) usually reads better: `[w.upper() for w in words]`. Both `map` and `filter` are lazy, so you need `list(...)` to see the items.

## `any`, `all`, `sum`, `zip`

```python
tasks = [{"done": True, "points": 3}, {"done": False, "points": 5}]

print(any(t["done"] for t in tasks))     # -> True    at least one is true
print(all(t["done"] for t in tasks))     # -> False   not all are true
print(sum(t["points"] for t in tasks))   # -> 8
```

`any` stops at the first true item. `all` stops at the first false item. This is called **short-circuiting**.

`zip` walks through several lists together (lesson 7). It stops at the **shortest** one. To get an error when the lengths differ, add `strict=True`:

```python
names = ["a", "b", "c"]
ids = [1, 2, 3]
print(dict(zip(ids, names)))               # -> {1: 'a', 2: 'b', 3: 'c'}   a dict from two lists
zip(ids, names[:2], strict=True)           # raises ValueError once it runs out
print(list(zip([1, 2, 3], ["a", "b"])))    # -> [(1, 'a'), (2, 'b')]
```

## `itertools`: tools for loops

The `itertools` module has many lazy tools:

```python
from itertools import accumulate, chain, combinations, count, islice, pairwise, product

print(list(chain([1, 2], [3])))              # -> [1, 2, 3]       join lists
print(list(islice(count(1), 3)))             # -> [1, 2, 3]       take 3 from an endless counter
print(list(accumulate([1, 2, 3])))           # -> [1, 3, 6]       running total
print(list(accumulate([3, 1, 2], min)))      # -> [3, 1, 1]       running smallest
print(list(pairwise([1, 4, 9])))             # -> [(1, 4), (4, 9)]
print(list(product("ab", [0, 1])))           # -> [('a', 0), ('a', 1), ('b', 0), ('b', 1)]
print(list(combinations([1, 2, 3], 2)))      # -> [(1, 2), (1, 3), (2, 3)]
```

`accumulate(items, function)` gives the running result: it calls `function(result_so_far, next_item)` for each item. Without a function, it adds.

### `groupby`: sort first!

`groupby` puts items with the same key into groups. But it only groups items that are **next to each other**. So you must **sort by the same key first**:

```python
from itertools import groupby
from operator import itemgetter

data = ["a", "b", "a"]
print([(k, len(list(g))) for k, g in groupby(data)])
# -> [('a', 1), ('b', 1), ('a', 1)]     "a" is split in two groups! it was not sorted

orders = [
    {"status": "paid", "amount": 10.0},
    {"status": "cancelled", "amount": 5.0},
    {"status": "paid", "amount": 2.5},
]
key = itemgetter("status")
for status, group in groupby(sorted(orders, key=key), key=key):
    items = list(group)
    print(status, len(items), sum(o["amount"] for o in items))
# -> cancelled 1 5.0
# -> paid 2 12.5
```

Forgetting to sort is the number one `groupby` bug. A `defaultdict` (below) is often simpler.

### `defaultdict`: a dict that fills in missing keys

`defaultdict(float)` (from `collections`) starts every new key at `0.0`, so you can add to it without checking:

```python
from collections import defaultdict

totals = defaultdict(float)
for item in [("tea", 2.5), ("cake", 4.0), ("tea", 1.0)]:
    name, price = item
    totals[name] += price
print(dict(totals))      # -> {'tea': 3.5, 'cake': 4.0}
```

To rank the results, sort the dict's `items()` with a key. Here: biggest total first, and equal totals by name:

```python
ranked = sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))
print(ranked)            # -> [('cake', 4.0), ('tea', 3.5)]
```

The `-kv[1]` puts the biggest total first. If two totals are equal, `kv[0]` (the name) breaks the tie from A to Z.

## `functools`: tools for functions

```python
from functools import partial, reduce

binary_to_int = partial(int, base=2)
print(binary_to_int("101"))      # -> 5
```

`partial(function, ...)` **pre-fills** some arguments and gives back a new function. It is handy for callbacks and for settings.

`reduce(function, items, start)` folds a list into **one** value. It calls `function(result_so_far, next_item)` for every item, starting with `start`:

```python
print(reduce(lambda acc, x: acc * x, [1, 2, 3, 4], 1))     # -> 24
print(reduce(lambda acc, ch: ch + acc, "abc", ""))         # -> cba   builds the text backwards
```

A loop, or `sum`, is usually clearer than `reduce`. But `reduce` is good for "pass a result from step to step".

### A little taste of `re`

`re.sub(pattern, replacement, text)` replaces all places in `text` that match a pattern. In the pattern `r"\s+"`, `\s` means "a space-like character" and `+` means "one or more":

```python
import re

print(re.sub(r"\s+", "-", "hello   big world"))    # -> hello-big-world
```

`partial` works well with it: `partial(re.sub, r"\s+", "-")` is a function that takes only the text.

String methods like `str.strip` and `str.lower` can also be used as plain functions: `str.strip("  hi ")` gives `'hi'`. So they fit into `map`, `key=` and `reduce` too.

## A little deeper (optional)

- `heapq.nlargest(3, items, key=...)` finds the top few items faster than sorting everything. It is good to mention in interviews.
- `lru_cache` and `cache` (lesson 23) are also in `functools`.

## Common mistakes

- Using `groupby` without sorting by the same key first.
- Writing `x = items.sort()`. It gives `None`, and you lose your data.
- Giving a lambda a name (`f = lambda ...`). Use `def`.
- Using a `map`, `filter` or `zip` result twice. It is used up after the first pass.
- Letting `zip` quietly cut off lists of different length. Use `strict=True` when the lengths must match.

## Interview corner

- **Q: How do you sort by two keys, one of them descending?** Use a tuple key and put a minus in front of the number: `(-age, name)`. Or sort twice.
- **Q: Is Python's sort stable? Why does it matter?** Yes. Items with equal keys keep their order, so sorting in several passes works.
- **Q: `groupby` gave wrong groups. Why?** The input was not sorted by the grouping key.
- **Q: `map` or a list comprehension?** The result is the same. Comprehensions read better. `map` is lazy and fine with an existing function.

## Summary

- Use `lambda` only for short keys and callbacks.
- `sorted(key=...)`, tuple keys, and `-number` for descending. `max` and `min` take `key` and `default`.
- `any` and `all` stop early. `zip(strict=True)` checks the lengths. `enumerate(start=1)` counts from 1.
- `itertools`: `chain`, `islice`, `count`, `accumulate`, `pairwise`, `product`, `combinations`, and `groupby` (after sorting).
- `functools`: `partial` pre-fills arguments, and `reduce` folds items into one value.

---
title: "Sets"
summary: "Sets for uniqueness, fast membership checks and set math."
plan_ids: []
---

A set holds **unique** values with no order. It is perfect for "have I seen this?" and "remove repeats".

## Create

```python
s = {1, 2, 3}
empty = set()          # {} is an empty dict, not a set
from_list = set([1, 1, 2, 2, 3])
print(from_list)       # -> {1, 2, 3}
print(len(from_list))  # -> 3
```

Items must be hashable: numbers, strings and tuples are fine; lists are not.

## Add, remove, test

```python
s = {1, 2}
s.add(3)
s.discard(1)           # no error if missing
print(s)               # -> {2, 3}
print(2 in s)          # -> True
```

`in` on a set is fast (about the same time for 10 or 10 million items). `in` on a list scans every item.

## Set math

```python
a = {1, 2, 3}
b = {2, 3, 4}
print(a | b)    # -> {1, 2, 3, 4}   union
print(a & b)    # -> {2, 3}         intersection
print(a - b)    # -> {1}            only in a
print(a ^ b)    # -> {1, 4}         in exactly one
```

Method forms: `a.union(b)`, `a.intersection(b)`, `a.difference(b)`, `a.symmetric_difference(b)`.

## Pattern: seen-set

```python
def first_repeat(items):
    seen = set()
    for x in items:
        if x in seen:
            return x
        seen.add(x)
    return None

print(first_repeat([3, 1, 4, 1, 5]))   # -> 1
```

## Duplicates trick

If `len(set(items)) != len(items)`, there is a duplicate.

```python
print(len(set([1, 2, 2])) != len([1, 2, 2]))   # -> True
```

## No order

Do not rely on the order of a set. Use `sorted(s)` to get an ordered list.

```python
print(sorted({3, 1, 2}))   # -> [1, 2, 3]
```

## Common mistakes

- `{}` makes a dict. Use `set()` for an empty set.
- Expecting order or indexing (`s[0]` is an error).
- Putting a list inside a set (unhashable). Use a tuple.
- Using `remove` on a missing item (error). `discard` is safe.

## Summary

- Sets: unique, unordered, fast `in`.
- `add`, `discard`, `|`, `&`, `-`, `^`.
- Seen-set pattern: check `in`, then `add`.
- `set(items)` removes repeats; `sorted(...)` to order the result.
- Reference: `reference/sets.md`.

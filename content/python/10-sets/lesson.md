---
title: Sets
summary: A set holds each value only once. Use it to remove duplicates, check "is it in here?" fast, and compare two groups.
plan_ids: []
---

A **set** is a collection of **unique** values with **no order**. Each value can be in a set only once. Use a set to remove duplicates, to check quickly whether something is in a group, and to compare two groups.

## Create a set

Use curly braces, or the `set()` function:

```python
tags = {"python", "api", "python"}
print(tags)        # -> {'python', 'api'}    the duplicate is gone (the order may differ)

nums = set([1, 2, 2, 3])     # make a set from a list
print(nums)        # -> {1, 2, 3}

empty = set()      # an empty set. Do NOT write {} - that is an empty dict.
```

A set can only hold **hashable** values. In short, that means numbers, strings and tuples (of those). Lists and dicts cannot go in a set, because they can change.

## Add, remove and check

```python
s = {1, 2}
s.add(3)             # now {1, 2, 3}
s.add(3)             # nothing changes, and there is no error
s.remove(2)          # KeyError if 2 is not in the set
s.discard(99)        # no error if 99 is not in the set
2 in s               # -> False
len(s)               # -> 2
```

`remove` and `discard` both remove an item. The difference: `remove` gives an error when the item is missing, and `discard` stays quiet.

Checking `x in my_set` is very fast, even for a huge set. On a list, Python has to look at the items one by one.

```python
allowed = {"admin", "editor"}
role = "editor"
if role in allowed:
    print("ok")      # -> ok
```

## Remove duplicates

Turning a list into a set is the easiest way to remove duplicates. Here is a step-by-step example: how many different names are in a list?

1. Turn the list into a set. The duplicates disappear.
2. Count the items with `len`.

```python
names = ["a", "b", "a", "c", "b"]
unique = set(names)
print(unique)                 # -> {'a', 'b', 'c'}
print(len(unique))            # -> 3
```

A set has no order, so the items can come out in any order. When you need a steady order, use `sorted(...)`. It gives back a list:

```python
print(sorted(unique))         # -> ['a', 'b', 'c']
```

## Set operations

Sets can be combined like circles in a Venn diagram:

```python
a = {1, 2, 3, 4}
b = {3, 4, 5}

a | b    # union (everything in either):          {1, 2, 3, 4, 5}
a & b    # intersection (in both):                {3, 4}
a - b    # difference (in a, but not in b):       {1, 2}
a ^ b    # symmetric difference (in only one):    {1, 2, 5}
```

The same operations also have method names: `a.union(b)`, `a.intersection(b)`, `a.difference(b)` and `a.symmetric_difference(b)`.

You can compare sets too:

```python
{1, 2} <= {1, 2, 3}       # -> True    subset (all of the first are in the second)
{1, 2, 3} >= {1}          # -> True    superset
{1, 2}.isdisjoint({3})    # -> True    nothing in common
```

An example with real data. Who came on which day?

```python
yesterday = {"ada", "linus", "guido"}
today = {"linus", "guido", "grace"}

print(today - yesterday)     # -> {'grace'}              new today
print(yesterday - today)     # -> {'ada'}                left
print(yesterday & today)     # -> {'linus', 'guido'}     came both days
```

You can mix sets with other tools. This gives all numbers from 1 to 5 that are not in a list:

```python
set(range(1, 6)) - {2, 4}    # -> {1, 3, 5}
```

## A little deeper (optional)

**Why is a set fast?** A set uses **hashing**. It turns each value into a number (a hash) and uses that number to know where to look. So it does not have to scan every item.

**Frozen sets.** A `frozenset` is a set that cannot change. It is hashable, so it can be a dict key or live inside another set. You will rarely need it.

## Common mistakes

- Writing `{}` and thinking it is an empty set. It is an empty dict. Use `set()`.
- Expecting an order, or writing `s[0]`. A set has no order, so this is a `TypeError`.
- Putting a list in a set: `{[1, 2]}` gives `TypeError: unhashable type: 'list'`.
- Using `remove` when the item may be missing. Use `discard`.
- Using a list for "is it in here?" checks on big data. A set is much faster.

## Summary

- A set stores unique, hashable values with no order.
- `set(items)` removes duplicates. `set()` makes an empty set.
- `add`, `remove` (error if missing), `discard` (no error) and `in` (fast).
- `|` union, `&` intersection, `-` difference, `^` symmetric difference.

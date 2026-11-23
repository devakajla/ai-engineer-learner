---
title: Tuples & unpacking
summary: A tuple is a fixed group of values. Learn how to make one and how to unpack it into names, which you will use everywhere in Python.
plan_ids: []
---

A **tuple** is like a list that cannot be changed after you make it. Use it for a small, fixed group of related values: a point `(x, y)`, a row from a database, or the two answers of a function.

## Create and read

Tuples use round brackets. You read them like lists:

```python
point = (3, 4)
point[0]        # -> 3
point[-1]       # -> 4
len(point)      # -> 2
point[0] = 9    # TypeError: 'tuple' object does not support item assignment
```

You can use indexing, slicing, `in`, `len`, `count` and `+`, just like with a list. But there is no `append`, `remove` or `sort`, because a tuple cannot change.

It is the **comma** that makes a tuple, not the brackets. So a tuple with one item needs a comma:

```python
a = 1, 2, 3      # -> (1, 2, 3)   brackets are optional
one = (5,)       # a tuple with one item (note the comma!)
not_tuple = (5)  # just the number 5
empty = ()
```

## Why use a tuple?

- It is **immutable**: nobody can change it by accident.
- It is **hashable** (if its items are). That means it can be a dictionary key or a set member (lessons 10 and 11). A list cannot.
- It says "this is a fixed record", not "a collection that will grow".

```python
visited = {(0, 0), (0, 1)}      # a set of coordinates
distance = {("A", "B"): 120}    # a dict with a pair as the key
```

## Unpacking

**Unpacking** means putting the items of a tuple into several names in one step:

```python
point = (3, 4)
x, y = point
print(x, y)    # -> 3 4

name, age, city = ("Dev", 25, "Delhi")
print(city)    # -> Delhi
```

The number of names must match the number of items. If not, you get a `ValueError`:

```python
a, b = (1, 2, 3)    # ValueError: too many values to unpack (expected 2)
```

### Swap two values

Unpacking gives a neat swap with no temporary variable:

```python
a, b = 1, 2
a, b = b, a
print(a, b)   # -> 2 1
```

Python builds the pair `(b, a)` first, and then unpacks it into `a` and `b`.

### Take the rest with `*`

A name with a star (`*rest`) collects "everything that is left" into a **list**:

```python
first, *rest = [1, 2, 3, 4]
print(first, rest)    # -> 1 [2, 3, 4]

*head, last = [1, 2, 3, 4]
print(head, last)     # -> [1, 2, 3] 4

first, *middle, last = [1, 2, 3, 4, 5]
print(middle)         # -> [2, 3, 4]
```

Note that `rest` is always a **list**, even when you unpack a tuple.

### Put items back together with `*`

The star also works when you **build** a tuple or a list. It spreads the items out:

```python
nums = [2, 3]
(1, *nums, 4)     # -> (1, 2, 3, 4)
[0, *nums]        # -> [0, 2, 3]
```

Here is a step-by-step example. Move the first item of a tuple to the end.

1. Take the first item and the rest: `first, *rest = t`.
2. Build a new tuple with the rest first, and `first` last: `(*rest, first)`.

```python
t = (1, 2, 3, 4)
first, *rest = t
(*rest, first)    # -> (2, 3, 4, 1)
```

### Skip a value with `_`

If you do not need a value, use the name `_` as a "throw away" name:

```python
_, y = (3, 4)         # we only want y
```

### Unpacking in a loop

```python
pairs = [("a", 1), ("b", 2)]
for letter, number in pairs:
    print(letter, number)
# -> a 1
# -> b 2
```

This is also what `enumerate` and `zip` give you in lesson 7.

## Returning two values

A function that "returns two values" really returns **one tuple**. You can unpack it right away:

```python
result = divmod(17, 5)     # a built-in function: (quotient, remainder)
print(result)              # -> (3, 2)
q, r = divmod(17, 5)       # unpack it
print(q, r)                # -> 3 2
```

You will write your own functions that return tuples in lesson 13. The idea is simple: `return a, b` makes a tuple.

## Changing between tuples and lists

```python
tuple([1, 2, 3])    # -> (1, 2, 3)
list((1, 2, 3))     # -> [1, 2, 3]
```

## A little deeper (optional)

**"Immutable" means the slots cannot change.** If a slot holds a list, that list can still change:

```python
t = ([1], 2)
t[0].append(9)
print(t)      # -> ([1, 9], 2)
```

This is also why a tuple that holds a list cannot be a dict key: it is not hashable.

**Named tuples** give each slot a name, so you can write `point.x`. They come from the `collections` module (lesson 14). Level 2 teaches dataclasses, which are similar.

## Common mistakes

- Writing `(5)` and thinking it is a tuple. Write `(5,)`.
- Trying to change a tuple item. Make a new tuple, or use a list if the data must change.
- Unpacking with the wrong number of names: `a, b = (1, 2, 3)` is a `ValueError`.
- Forgetting that `*rest` always gives a **list**.

## Summary

- A tuple is an ordered group that cannot change. The comma makes it.
- Tuples can be dict keys and set members. Lists cannot.
- Unpack with `a, b = pair`. Swap with `a, b = b, a`.
- `first, *rest = items` and `*head, last = items` collect the remaining items into a list. `(*rest, first)` builds a tuple back together.
- Use `_` for values you do not need.

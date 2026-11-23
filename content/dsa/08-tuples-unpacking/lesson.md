---
title: "Tuples and unpacking"
summary: "Tuples, unpacking, swapping, zip, and returning several values."
plan_ids: []
---

A tuple is like a list that cannot change. Use it for small fixed groups of values: a point `(x, y)`, a pair `(name, age)`, or several return values.

## Create and read

```python
point = (3, 4)
print(point[0], point[1])   # -> 3 4
print(len(point))           # -> 2
single = (5,)               # the comma makes it a tuple
print(type(single))         # -> <class 'tuple'>
```

Tuples are immutable: `point[0] = 9` is an error.

## Unpacking

```python
x, y = (3, 4)
print(x, y)    # -> 3 4

name, age = "Asha", 30
print(name)    # -> Asha
```

The number of names must match the number of items.

## Swap without a temp variable

```python
a, b = 1, 2
a, b = b, a
print(a, b)   # -> 2 1
```

Swapping two list items works the same way: `nums[i], nums[j] = nums[j], nums[i]`.

## Star unpacking

```python
first, *rest = [1, 2, 3, 4]
print(first, rest)   # -> 1 [2, 3, 4]
*init, last = [1, 2, 3, 4]
print(init, last)    # -> [1, 2, 3] 4
```

## Return several values

```python
def min_max(nums):
    return min(nums), max(nums)

low, high = min_max([4, 1, 9])
print(low, high)   # -> 1 9
```

## `zip`: walk two lists together

```python
names = ["a", "b", "c"]
scores = [10, 20, 30]
for n, s in zip(names, scores):
    print(n, s)
# -> a 10
# -> b 20
# -> c 30
print(list(zip(names, scores)))   # -> [('a', 10), ('b', 20), ('c', 30)]
```

`zip` stops at the shorter list.

## Tuples as dictionary keys / set items

Because they cannot change, tuples can be dictionary keys and set members. Lists cannot.

```python
seen = {(1, 2), (3, 4)}
print((1, 2) in seen)   # -> True
```

You will use dictionaries and sets in the next lessons.

## Common mistakes

- `(5)` is just the number 5. Use `(5,)`.
- Unpacking with the wrong count: `a, b = (1, 2, 3)` raises `ValueError`.
- Trying to change a tuple in place.

## Summary

- Tuples are fixed groups. Unpack with `a, b = pair`.
- Swap with `a, b = b, a`.
- Return many values as a tuple.
- `zip` pairs two lists; `*rest` collects the rest.
- Reference: `reference/tuples.md`.

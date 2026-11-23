---
title: Lists
summary: A list holds many values in order, and you can change it. Learn indexing, slicing, the common methods, sorting and copying.
plan_ids: []
---

A **list** holds many values in one place, in order. A list of names, a list of prices, a list of tasks: lists are the most used container in Python. A list can change after you make it (it is **mutable**), so you can add, remove and replace items.

## Create and read

Write the items inside square brackets, with commas between them.

```python
nums = [10, 20, 30, 40]
nums[0]      # -> 10    the first item (the index starts at 0)
nums[-1]     # -> 40    the last item (a negative index counts from the end)
len(nums)    # -> 4     how many items
20 in nums   # -> True  is 20 in the list?
nums[10]     # IndexError: list index out of range
```

A list can hold any kind of value, and even a mix. In practice a list usually holds items of one kind.

You can loop over a list (lesson 7), and you can make an empty list:

```python
total = 0
for n in [10, 20, 30]:
    total += n
print(total)    # -> 60

empty = []
```

## Slicing

Slicing works like it does for strings (lesson 4). `items[start:stop:step]` gives a **new list**. It stops **before** `stop`, and it never raises `IndexError`.

```python
nums = [10, 20, 30, 40, 50]
nums[1:3]     # -> [20, 30]
nums[:2]      # -> [10, 20]
nums[3:]      # -> [40, 50]
nums[-2:]     # -> [40, 50]
nums[::2]     # -> [10, 30, 50]
nums[::-1]    # -> [50, 40, 30, 20, 10]   a reversed copy
```

## Changing a list

Because lists are mutable, their methods change the list itself. Most of them give back `None`.

```python
fruits = ["apple", "banana"]
fruits.append("cherry")          # add at the end
fruits.insert(0, "kiwi")         # add at a position
fruits.extend(["fig", "plum"])   # add many items
print(fruits)   # -> ['kiwi', 'apple', 'banana', 'cherry', 'fig', 'plum']

fruits[1] = "avocado"            # replace one item
fruits.remove("fig")             # remove the first "fig"
last = fruits.pop()              # remove and give back the last item -> 'plum'
first = fruits.pop(0)            # remove and give back index 0 -> 'kiwi'
del fruits[0]                    # delete by index
```

| Method | What it does |
|---|---|
| `append(x)` | add one item at the end |
| `extend(items)` | add every item of another list |
| `insert(i, x)` | add `x` at position `i` |
| `remove(x)` | remove the first `x` (`ValueError` if it is missing) |
| `pop(i)` | remove the item at `i` (the last one if you give no `i`) and give it back |
| `index(x)` | the position of the first `x` |
| `count(x)` | how many times `x` is in the list |
| `reverse()` | reverse the list in place |
| `sort()` | sort the list in place |

### `append`, `extend` and `+`

```python
a = [1, 2]
a.append([3, 4])      # -> a is [1, 2, [3, 4]]   one item, and it is a list
b = [1, 2]
b.extend([3, 4])      # -> b is [1, 2, 3, 4]
c = [1, 2] + [3, 4]   # -> [1, 2, 3, 4]    + makes a new list
```

## Building a new list

A very common job: go through a list and make a new one. Start with an empty list, then `append` in a loop. A step-by-step example: keep only the even numbers.

1. Start with an empty list: `evens = []`.
2. Loop over the numbers.
3. If a number is even, `append` it.
4. The original list stays unchanged.

```python
nums = [3, 8, 5, 6]
evens = []
for n in nums:
    if n % 2 == 0:
        evens.append(n)
print(evens)    # -> [8, 6]
print(nums)     # -> [3, 8, 5, 6]
```

Use `not in` when you want to add an item only if it is not there yet:

```python
seen = []
for n in [1, 2, 1]:
    if n not in seen:
        seen.append(n)
print(seen)     # -> [1, 2]
```

## Sorting

```python
nums = [3, 1, 2]
nums.sort()                      # sorts the list itself and gives back None
print(nums)                      # -> [1, 2, 3]

print(sorted([3, 1, 2]))                  # -> [1, 2, 3]   a new list, the old one is untouched
print(sorted([3, 1, 2], reverse=True))    # -> [3, 2, 1]

words = ["pear", "fig", "banana"]
print(sorted(words, key=len))             # -> ['fig', 'pear', 'banana']
```

`key=len` means "sort by the length of each item". The word lengths are 4, 3, 6, so the order is `fig`, `pear`, `banana`.

A classic bug is `nums = nums.sort()`. The `sort` method gives back `None`, so `nums` becomes `None`.

## Useful built-in functions

```python
nums = [4, 1, 7]
len(nums)     # -> 3
sum(nums)     # -> 12
min(nums)     # -> 1
max(nums)     # -> 7
```

## Copying a list

`b = a` does **not** copy a list. It gives the same list a second name (remember "two names, one value" from lesson 2).

```python
a = [1, 2, 3]
b = a            # NOT a copy: two names, one list
b.append(4)
print(a)         # -> [1, 2, 3, 4]

c = a.copy()     # a real copy (also: a[:] or list(a))
c.append(5)
print(a)         # -> [1, 2, 3, 4]   a is unchanged
```

Functions that must **not** change the list they receive should work on a copy, or build a new list.

## Lists inside lists

```python
grid = [[1, 2], [3, 4]]
grid[1][0]    # -> 3     row 1, then item 0
```

## A little deeper (optional)

**A copy is shallow.** `copy()` makes a new outer list, but any list **inside** is still shared with the original. Level 2 shows how to make a deep copy.

**A trap with grids.** `[[0] * 3] * 3` makes three names for the same row. Changing one row changes all of them. Build each row separately, in a loop.

**Speed.** `pop(0)` and `insert(0, x)` are slow on big lists, because every other item has to move over.

## Common mistakes

- Writing `x = x.sort()` or `x = x.append(1)`. These methods give back `None`.
- Using `b = a` and expecting a copy.
- Removing items from a list while looping over the same list.
- Calling `remove(x)` when `x` is not in the list. This is a `ValueError`. Check with `in` first.

## Summary

- A list is ordered and can change. Index from `0`, and negative indexes count from the end.
- A slice `a[i:j:k]` gives a new list.
- `append`, `extend`, `insert`, `remove`, `pop`, `sort` and `reverse` change the list and give back `None` (except `pop`, which gives back the item).
- `sorted(x, key=..., reverse=...)` gives a new sorted list.
- `b = a` shares the list. Use `a.copy()` or `a[:]` to copy.

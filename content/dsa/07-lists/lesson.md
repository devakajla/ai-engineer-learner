---
title: "Lists"
summary: "Indexing, slicing, common list methods, sorting, and the loop patterns for list problems."
plan_ids: []
---

A list holds items in order and can change. Most array-style problems use lists.

## Indexing and slicing

```python
nums = [10, 20, 30, 40, 50]
print(nums[0])      # -> 10
print(nums[-1])     # -> 50
print(nums[1:3])    # -> [20, 30]
print(nums[::-1])   # -> [50, 40, 30, 20, 10]
```

A slice makes a **new** list.

## Change a list

```python
items = [1, 2, 3]
items.append(4)         # add at the end
items.insert(0, 0)      # add at an index
items.remove(2)         # remove first value 2
last = items.pop()      # remove and return the last item
print(items, last)      # -> [0, 1, 3] 4
items[0] = 99
print(items)            # -> [99, 1, 3]
```

> `append`, `insert`, `remove`, `pop` and `sort` change the list and return `None`. Do not write `x = x.append(1)`.

## Useful built-ins

```python
nums = [4, 1, 7]
print(len(nums), sum(nums), min(nums), max(nums))   # -> 3 12 1 7
print(sorted(nums))     # -> [1, 4, 7]  (new list)
nums.sort()             # sorts in place
print(nums)             # -> [1, 4, 7]
print(sorted(nums, reverse=True))   # -> [7, 4, 1]
print(7 in nums)        # -> True
```

## `enumerate`: index and value together

```python
for i, v in enumerate(["a", "b", "c"]):
    print(i, v)
# -> 0 a
# -> 1 b
# -> 2 c
```

## Loop patterns on lists

**Track the best so far** (you do not need `max`):

```python
def largest(nums):
    best = nums[0]
    for n in nums:
        if n > best:
            best = n
    return best
```

**Build a new list:**

```python
def only_positive(nums):
    result = []
    for n in nums:
        if n > 0:
            result.append(n)
    return result

print(only_positive([3, -1, 4]))   # -> [3, 4]
```

**Running total:**

```python
total = 0
sums = []
for n in [1, 2, 3]:
    total += n
    sums.append(total)
print(sums)   # -> [1, 3, 6]
```

## Two indexes

Use `i` and `j` to walk two places in one list, or two lists at once:

```python
nums = [1, 2, 3, 4]
i, j = 0, len(nums) - 1
while i < j:
    nums[i], nums[j] = nums[j], nums[i]
    i += 1
    j -= 1
print(nums)   # -> [4, 3, 2, 1]
```

## Common mistakes

- `IndexError`: using `nums[len(nums)]` or indexing an empty list.
- Changing a list while looping over it.
- Using the result of `sort()` or `append()` (it is `None`).
- Copying with `b = a`: both names point to the same list. Use `a[:]` or `a.copy()`.

## Summary

- Index, slice, `append insert remove pop sort`.
- `len sum min max sorted in enumerate`.
- Patterns: best so far, build a new list, running total, two indexes.
- Slices and `sorted` make new lists; `sort` and `append` change the list in place.
- Reference: `reference/lists.md`.

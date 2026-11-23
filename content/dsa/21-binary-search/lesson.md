---
title: "Binary search"
summary: "Halve the search range each step: on sorted lists, on shapes, and on the answer itself."
plan_ids: []
---

Binary search is not only "find a number in a sorted list". It is a way to **guess an answer with yes/no feedback**. Each check throws away half of the possibilities, so n items need only about log2(n) steps (1,000,000 items: about 20 steps).

> Watch the intro video first. Exercises 01 to 11 have video segments.

## When to think "binary search"

- Sorted data, or rotated sorted data.
- A **shape** (mountain, peak) where one comparison tells you which side to keep.
- "Smallest X such that ..." or "largest X such that ..." where a bigger X makes the check easier (or harder) in **one direction only**.
- You need better than O(n).

## The classic template

```python
def binary_search(nums, target):
    lo, hi = 0, len(nums) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            lo = mid + 1        # target is on the right
        else:
            hi = mid - 1        # target is on the left
    return -1

print(binary_search([1, 3, 5, 7], 5))   # -> 2
```

## Template 2: first True (lower bound)

Many problems fit one yes/no check that flips once: `False False False True True`. Find the first `True`:

```python
lo, hi = 0, len(items)          # hi is one past the end: "none" is a valid answer
while lo < hi:
    mid = (lo + hi) // 2
    if check(mid):
        hi = mid                # mid could be the answer: keep it
    else:
        lo = mid + 1            # mid is not the answer: drop it
# lo is the first index where check is True (or len(items))
```

With `lo < hi` the range never becomes empty, so no infinite loop as long as one side moves past `mid` (`mid + 1`) and the other keeps `mid`.

## Pattern: first / last position and counting

On duplicates, when you find `target` save the index and keep going **left** (first) or **right** (last). Count = `first_ge(t + 1) - first_ge(t)`.

## Pattern: shapes (mountain, peak, rotated)

Compare `mid` with a neighbour or with an end, and keep the half that must contain the answer.

```python
# mountain peak
if arr[mid] < arr[mid + 1]:
    lo = mid + 1        # still going up: peak is on the right
else:
    hi = mid
```

Rotated list: at any `mid` **one half is sorted**. Find it, test if the target is inside it, else go to the other half.

## Pattern: binary search on the answer

Do not search a list. Search the **range of possible answers**.

1. Find the smallest and biggest possible answer (`lo`, `hi`).
2. Write `works(x)`: a simple O(n) check.
3. Make sure it flips once (if `x` works, `x + 1` also works, or the opposite).
4. Binary search with `works`.

```python
def min_eating_speed(piles, h):
    lo, hi = 1, max(piles)
    while lo < hi:
        mid = (lo + hi) // 2
        hours = sum((p + mid - 1) // mid for p in piles)   # ceil(p / mid)
        if hours <= h:
            hi = mid
        else:
            lo = mid + 1
    return lo

print(min_eating_speed([3, 6, 7, 11], 8))   # -> 4
```

Aggressive cows, book allocation, ship packages, smallest divisor: same shape. Maximise-the-minimum problems flip the other way (`works` -> try bigger, `lo = mid + 1`).

## Pattern: matrices

- Fully chained rows (row start > previous row end): treat as one list, `row, col = divmod(mid, cols)`.
- Rows and columns sorted separately: start at the top-right corner and walk (staircase).
- K-th smallest: binary search the **value**, count items `<= mid`.

## Common mistakes

- Off-by-one: `lo <= hi` with `hi = mid - 1`, or `lo < hi` with `hi = mid`. Do not mix the two styles.
- Infinite loop when `lo = mid` instead of `mid + 1`.
- Wrong search range for answer problems (`lo` too big or `hi` too small).
- `mid = (lo + hi) // 2` is fine in Python (no overflow), but in C++ or Java use `lo + (hi - lo) / 2`.
- Using binary search when the check does not flip only once.
- Not testing empty and one-item inputs.

## Interview corner

**Q: Why O(log n)?**
A: The range halves each step: n, n/2, n/4, ... 1.

**Q: How do you know a problem is "binary search on the answer"?**
A: The question asks for the min or max value of something, and a simple check tells yes/no for a guess, in one direction only.

**Q: Search in a rotated sorted list: how?**
A: One half around `mid` is always sorted. Check if the target lies in the sorted half; keep that half, else the other.

**Q: How to handle duplicates?**
A: Do not stop at the first hit. Save it and continue left or right, depending on first or last.

## Summary

- Halve the range each step: O(log n).
- Two templates: classic (`lo <= hi`) and first-True (`lo < hi`, `hi = mid`).
- Shapes: compare with a neighbour or end. Answers: write a `works(x)` check and search the range.
- Cheat sheet: `reference/patterns.md`.

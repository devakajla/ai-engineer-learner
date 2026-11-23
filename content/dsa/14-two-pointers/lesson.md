---
title: "Two pointers"
summary: "Walk a list with two indexes to turn O(n²) pair searches into O(n) with no extra space."
plan_ids: []
---

Many problems ask you to look at **pairs** or to **rearrange** a list. The brute force checks every pair: O(n²). With **two pointers** you keep two indexes and move them in a smart way, so one pass is enough: O(n), and often **O(1) extra space**.

> Watch the intro video at the top first (the flow chart for spotting the pattern). Each exercise has a video segment where the same problem is solved. Code there may be C++/Java; yours is Python.

## When to think "two pointers"

Signals in the question:

1. The data is a **sorted array or string** (or sorting it first helps).
2. You must find a **pair / triplet / quadruplet** with a condition.
3. Words like **merge, remove duplicates, rearrange, reverse, palindrome**.
4. The question says **O(1) extra space** or "in place".

> Two pointers is **not** sliding window. Sliding window (next lesson) tracks a *range*; two pointers track *two positions*.

## Type 1: two ends, move inward

Put `left` at the start and `right` at the end. Look at the sum. If it is too small, only a bigger left value can help, so `left += 1`. If it is too big, `right -= 1`.

```python
def two_sum_sorted(nums, target):
    left, right = 0, len(nums) - 1
    while left < right:
        s = nums[left] + nums[right]
        if s == target:
            return [left, right]
        if s < target:
            left += 1         # need a bigger sum
        else:
            right -= 1        # need a smaller sum
    return []

print(two_sum_sorted([1, 2, 4, 7, 11], 9))   # -> [1, 3]
```

Why is it correct? Because the list is sorted. If `nums[left] + nums[right]` is too small, then `nums[left]` with *any* smaller right value is even smaller, so `nums[left]` can never be part of the answer and we can drop it. Each step drops one item, so the loop runs at most `n` times.

> If the array is **not sorted** and you need the values (not the indexes), sort first: O(n log n) and still no extra set.

## Type 2: same direction, a "writer" and a "reader"

`fast` reads every item. `slow` marks where the next good item should be written. This removes or moves things **in place**.

```python
def remove_duplicates(nums):          # nums is sorted
    if not nums:
        return 0
    slow = 1                          # next write position
    for fast in range(1, len(nums)):
        if nums[fast] != nums[fast - 1]:
            nums[slow] = nums[fast]
            slow += 1
    return slow

data = [1, 1, 2, 2, 3]
k = remove_duplicates(data)
print(k, data[:k])                    # -> 3 [1, 2, 3]
```

## Type 3: two lists, one pointer each (merge)

```python
def merge_sorted(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])                 # one list may have items left
    out.extend(b[j:])
    return out

print(merge_sorted([1, 3, 5], [2, 4]))   # -> [1, 2, 3, 4, 5]
```

After every step **at least one pointer moves**. If both could stay, the loop might never end.

## Type 4: fix one, two-pointer the rest (3Sum)

For "find triplets": sort, fix `i`, then run Type 1 on the part to the right of `i`. Total O(n²) instead of O(n³). Skip repeated values so you do not return the same triplet twice.

```python
def three_sum_exists(nums):
    nums = sorted(nums)
    for i in range(len(nums) - 2):
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                return True
            if s < 0:
                left += 1
            else:
                right -= 1
    return False

print(three_sum_exists([-1, 0, 1, 5]))   # -> True
```

## Type 5: three pointers (Dutch flag)

To sort only `0`, `1`, `2` in one pass, keep `low` (next place for 0), `high` (next place for 2) and `mid` (reader). Swap items into place with tuple swap `a[i], a[j] = a[j], a[i]`.

```python
def sort_colors(nums):
    low, mid, high = 0, 0, len(nums) - 1
    while mid <= high:
        if nums[mid] == 0:
            nums[low], nums[mid] = nums[mid], nums[low]
            low += 1
            mid += 1
        elif nums[mid] == 2:
            nums[mid], nums[high] = nums[high], nums[mid]
            high -= 1                 # do NOT move mid: the swapped item is unchecked
        else:
            mid += 1

data = [2, 0, 1, 2, 0]
sort_colors(data)
print(data)                           # -> [0, 0, 1, 2, 2]
```

## Template cheat sheet

| Type | Start | Move | Use for |
| --- | --- | --- | --- |
| Opposite ends | `0` and `n-1` | toward each other | sum of pair, palindrome, container |
| Reader/writer | both at start | `fast` always, `slow` sometimes | remove, move zeroes |
| Two lists | one per list | the smaller one | merge |
| Fix + pair | `i`, then `i+1` and `n-1` | inner pair | 3Sum, 4Sum |
| Three pointers | `low, mid, high` | by value | Dutch flag |

## Common mistakes

- Running two pointers on an **unsorted** list when the logic needs sorted order.
- `while left <= right` when it must be `left < right` (you would pair an item with itself).
- Forgetting to move a pointer in some branch: infinite loop.
- Returning duplicate triplets: skip equal neighbours after you find an answer.
- In Dutch flag, moving `mid` after swapping with `high`.

## Interview corner

- **Q: Why does two pointers on a sorted array work for pair sum?** Moving the pointer on the wrong side can never help, so each step safely discards one item. That makes it O(n).
- **Q: Hash map vs two pointers for Two Sum?** Hash map: O(n) time, O(n) space, works unsorted. Two pointers: O(1) space, needs sorted data (sorting costs O(n log n)).
- **Q: Time complexity of 3Sum with two pointers?** O(n²): sort is O(n log n), then n times an O(n) pair scan.
- **Q: How do you avoid duplicate triplets?** Sort, then skip a value equal to the previous one for `i`, and skip equal neighbours for `left` and `right` after a hit.

## Summary

- Two pointers = two indexes moved by a rule; O(n) time, usually O(1) space.
- Types: opposite ends, reader/writer, two lists, fix + pair, three pointers.
- Sorted data is the main signal; sort first if only values are needed.
- Every loop step must move at least one pointer.
- Revision video: <https://www.youtube.com/watch?v=n7v0SokbF4I>. Reference: `reference/patterns.md`.

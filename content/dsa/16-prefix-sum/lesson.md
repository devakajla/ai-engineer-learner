---
title: "Prefix sum"
summary: "Pre-compute running totals once, then answer any range-sum question in O(1)."
plan_ids: []
---

Many questions ask for the **sum of a range** again and again, or for subarrays with a given sum. Adding the range each time costs O(n) per question. With a **prefix sum** you prepare once in O(n) and every range sum costs O(1).

> Watch the intro video at the top first. The playlist teaches prefix sum in one video, so the exercises here are written for this app (no video segment per exercise).

## The idea

`prefix[i]` is the sum of the first `i` items. Put a `0` at the front so `prefix[0] = 0`.

```python
nums = [2, 4, 1, 6, 3]
prefix = [0]
for x in nums:
    prefix.append(prefix[-1] + x)
print(prefix)                   # -> [0, 2, 6, 7, 13, 16]
```

The sum of `nums[left..right]` (both included) is a **difference**:

```python
left, right = 1, 3
print(prefix[right + 1] - prefix[left])   # -> 11   (4 + 1 + 6)
```

Why? `prefix[right + 1]` has everything up to `right`. `prefix[left]` is the part before `left`. Subtract, and only the range stays.

> The leading `0` removes the special case for `left = 0`.

## Prefix sum with the total (left and right sides)

You often need "sum on the left" and "sum on the right" of an index. Keep a running `left`, and get the right side from the total:

```python
nums = [1, 7, 3, 6, 5, 6]
total = sum(nums)
left = 0
for i, x in enumerate(nums):
    right = total - left - x
    if left == right:
        print(i)                # -> 3
    left += x
```

## Prefix sum + dict: count subarrays with sum k

A subarray sum is `prefix[j] - prefix[i]`. At position `j`, you want an earlier prefix equal to `prefix[j] - k`. So keep a dict of **how many times** each prefix value was seen.

```python
def subarray_sum_k(nums, k):
    seen = {0: 1}                   # empty prefix
    total = 0
    count = 0
    for x in nums:
        total += x
        count += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return count

print(subarray_sum_k([1, 2, 3], 3))   # -> 2
```

This works with **negative numbers**, where sliding window fails. It is O(n).

For the **longest** subarray, store the **first index** of each prefix value instead of a count (only save it the first time you see it).

## Remainders and the 0/1 trick

- "Sum divisible by k": two prefixes with the **same remainder** `% k` have a divisible part between them.
- "Equal 0s and 1s": change every `0` to `-1`, then it is "sum equals 0".

## Difference array (the reverse trick)

To add `v` to a whole range many times, mark only the ends, then take one running sum.

```python
n = 5
diff = [0] * (n + 1)
diff[1] += 2; diff[3 + 1] -= 2       # add 2 to indexes 1..3
result, run = [], 0
for i in range(n):
    run += diff[i]
    result.append(run)
print(result)                         # -> [0, 2, 2, 2, 0]
```

## 2D prefix sum

`P[i+1][j+1]` is the sum of the rectangle from `(0,0)` to `(i,j)`. A rectangle query is `big - top strip - left strip + corner` (the corner was removed twice).

## Prefix and suffix products

"Product of everything except me" without division: one pass for the product **before** each item, one pass for the product **after**.

## Common mistakes

- Forgetting the leading `0`, which breaks ranges that start at index 0.
- Off-by-one: the sum of `[left..right]` is `prefix[right + 1] - prefix[left]`.
- Forgetting `seen = {0: 1}` in the dict version (misses subarrays that start at index 0).
- In the "longest" version, overwriting the first index. Keep the earliest one.
- Using `%` in other languages with negative numbers. In Python `-3 % 5 == 2`, which is what you want.

## Interview corner

**Q: When do you use prefix sum instead of sliding window?**
A: When the numbers can be negative, or when you have many range queries. Sliding window needs a rule that only goes one way.

**Q: Why `seen = {0: 1}`?**
A: It represents the empty prefix. Without it you miss subarrays that start at index 0.

**Q: Time and space of the subarray-sum-k trick?**
A: O(n) time and O(n) space for the dict.

**Q: How do you do many range additions fast?**
A: A difference array: mark `+v` at the start and `-v` after the end, then one running sum.

## Summary

- `prefix[i]` = sum of the first `i` items, with `prefix[0] = 0`. Range sum = `prefix[r + 1] - prefix[l]`.
- Left and right sides: `right = total - left - x`.
- Count subarrays with sum `k`: counter-dict of prefixes. Longest: first-index dict.
- Remainder dict for "divisible by k"; `0 -> -1` for equal 0s and 1s.
- Difference array = prefix sum in reverse (many range updates).
- Works with negatives. Cheat sheet: `reference/patterns.md`.

---
title: "Kadane's algorithm"
summary: "Track the best subarray that ends at the current item, and turn many max/min subarray questions into one pass."
plan_ids: []
---

Kadane's algorithm solves "find the **best contiguous part**" in O(n). Instead of trying every start and end (O(n²) or O(n³)), at each index you answer a smaller question:

> What is the best subarray that **ends here**?

Then the overall answer is the best of those.

> Watch the intro video first. Exercises 01 to 04 have video segments. Video 44 of the playlist explains "one deletion" again more slowly: https://www.youtube.com/watch?v=jIz4zcFuUU8

## The idea

Standing at `x`, the best subarray that ends at `x` is **one of two things**:

1. `x` alone (start fresh), or
2. `x` joined to the best subarray that ended just before (extend).

```python
def max_subarray(nums):
    ending_here = best = nums[0]
    for x in nums[1:]:
        ending_here = max(x, ending_here + x)   # start fresh or extend
        best = max(best, ending_here)
    return best

print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))   # -> 6
```

Extending is only a good idea if the old running part is **positive**. If it is negative, it only drags you down, so start fresh.

> Start with `nums[0]`, not `0`. If all numbers are negative the answer is the biggest negative number, not 0.

## The 3 steps for any Kadane question

1. Define `ending_here`: the best result for a part that **must end at index i**.
2. Write how it comes from the previous one (fresh start or extend).
3. The answer is the best `ending_here` over all `i`.

## Variants

| Question | What changes |
| --- | --- |
| minimum sum | swap `max` and `min` |
| maximum product | track **both** max and min (a negative can flip) |
| one deletion allowed | two states: `keep` (nothing deleted) and `deleted` |
| circular array | answer is `max(max_sub, total - min_sub)`; if all negative return `max_sub` |
| max absolute sum | run max and min together, allow empty |
| streak questions (increasing run, turbulent, mountain) | `run = run + 1` if the rule holds else restart |
| length at least k | prefix sums plus a running minimum |

### Max product: keep max and min

```python
def max_product(nums):
    hi = lo = best = nums[0]
    for x in nums[1:]:
        candidates = (x, hi * x, lo * x)
        hi, lo = max(candidates), min(candidates)
        best = max(best, hi)
    return best

print(max_product([2, 3, -2, 4]))   # -> 6
```

### One deletion: two states

```python
keep = nums[0]               # best ending here, nothing deleted
deleted = float("-inf")      # best ending here, one element deleted
for x in nums[1:]:
    deleted = max(keep, deleted + x)    # delete x now, or delete something earlier
    keep = max(x, keep + x)
```

### Circular: total minus the worst middle

A wrapping part is "everything except a middle part". Remove the **smallest** middle part: `total - min_subarray`.

## Kadane vs prefix sum vs sliding window

- **Kadane**: max or min of a sum / product over any subarray.
- **Sliding window**: a rule about the window (like "at most k distinct") with positive values.
- **Prefix sum + dict**: count or find a subarray with an **exact** sum.

## Common mistakes

- Starting `best` at `0` (wrong when all numbers are negative).
- Forgetting that for products a negative number can turn the smallest product into the biggest.
- In the circular case, returning `total - min_sub` when every number is negative (that part would be empty).
- Mixing up subarray (contiguous) and subsequence (not contiguous).
- Updating `best` before updating `ending_here`.

## Interview corner

**Q: Explain Kadane in one sentence.**
A: For each index keep the best sum of a subarray ending there: either start fresh or extend the previous one, and remember the overall best.

**Q: Time and space?**
A: O(n) time and O(1) space.

**Q: How do you also return the start and end indexes?**
A: Remember where the current run started (reset it when you start fresh), and save `(start, end)` whenever you update `best`.

**Q: Why does max product need two variables?**
A: A negative number turns the smallest (most negative) product into the biggest, so you must track both ends.

**Q: Circular max subarray?**
A: Either the best normal subarray, or the total minus the smallest subarray (the wrapping case). Handle the all-negative case separately.

## Summary

- Kadane: best subarray **ending at i** = fresh start or extend. Answer = best over all i. O(n) time, O(1) space.
- Start from `nums[0]` so all-negative lists work.
- Product: track max and min. One deletion: two states. Circular: `total - min_sub`.
- Streak questions use the same "extend or restart" idea.
- Cheat sheet: `reference/patterns.md`.

---
title: "Sliding window"
summary: "Slide a range over a list or string and update its answer one step at a time, instead of recounting it."
plan_ids: []
---

Many questions ask about a **subarray** or **substring**: a continuous part of a list or string. The brute force looks at every start and every end: O(n²) or worse, and it recounts the same items again and again.

A **sliding window** keeps a range `[lo..hi]` and moves it right. When the window moves one step, only one item enters and one item leaves. So you **update** the answer in O(1) and the whole job is O(n).

> Watch the intro video at the top first. Each exercise has a video segment where the same problem is solved (code there may be C++/Java; yours is Python).

## When to think "sliding window"

1. The question is about a **continuous** subarray or substring.
2. It asks for the **longest / shortest / maximum / minimum / count** of such a part.
3. There is a condition on the part: "sum at most k", "no repeated letters", "at most 2 types".

> Subarray and substring are continuous. A *subsequence* is not. Subsequence questions are usually not sliding window.

## The 4 questions (video flow chart)

For any window problem, answer these in order:

1. **Fixed or variable size?** "of size k" means fixed. "longest / shortest" means variable.
2. **What is the window?** `lo` and `hi` pointers.
3. **What information do you store?** A running sum, a counter-dict, a set, a number of zeros.
4. **Is the window valid?** If not, move `lo` until it is valid again.

## Type 1: fixed-size window

The size is given (`k`). Build the first window, then slide: add the new item, remove the old one.

```python
def max_sum_window(nums, k):
    total = sum(nums[:k])             # first window
    best = total
    for i in range(k, len(nums)):
        total += nums[i] - nums[i - k]   # one in, one out
        best = max(best, total)
    return best

print(max_sum_window([2, 1, 5, 1, 3, 2], 3))   # -> 9
```

Brute force would add `k` numbers for every window: O(n·k). Sliding makes it O(n).

## Type 2: variable window, find the **maximum**

Grow `hi` every step. If the window becomes **invalid**, shrink from `lo` until it is valid. The answer is the best length you saw.

```python
def longest_unique(s):
    counts = {}
    lo = 0
    best = 0
    for hi, ch in enumerate(s):
        counts[ch] = counts.get(ch, 0) + 1
        while counts[ch] > 1:            # invalid: a repeat
            counts[s[lo]] -= 1
            lo += 1
        best = max(best, hi - lo + 1)    # window is valid here
    return best

print(longest_unique("abcabcbb"))   # -> 3
```

## Type 3: variable window, find the **minimum**

Grow `hi` until the window is **valid**. Then shrink while it **stays** valid, and record the length each time.

```python
def min_len_subarray(nums, target):      # positive numbers
    best = 0
    lo = 0
    total = 0
    for hi in range(len(nums)):
        total += nums[hi]
        while total >= target:           # valid: try to make it smaller
            length = hi - lo + 1
            if best == 0 or length < best:
                best = length
            total -= nums[lo]
            lo += 1
    return best

print(min_len_subarray([2, 3, 1, 2, 4, 3], 7))   # -> 2
```

> **The one rule that decides everything:**
> - **Maximum** window: shrink **while invalid**, then record.
> - **Minimum** window: record **while valid**, and shrink inside that loop.

## Type 4: counting windows

To count all valid subarrays, notice: if `[lo..hi]` is valid, then **every** start from `lo` to `hi` is valid for the end `hi`. That is `hi - lo + 1` subarrays. Add it at every step.

```python
def count_product_less(nums, k):         # positive numbers
    if k <= 1:
        return 0
    product, lo, count = 1, 0, 0
    for hi, x in enumerate(nums):
        product *= x
        while product >= k:
            product //= nums[lo]
            lo += 1
        count += hi - lo + 1
    return count

print(count_product_less([10, 5, 2, 6], 100))   # -> 8
```

## Choosing what to store

| Question | Window info |
| --- | --- |
| sum of the window | one number `total` |
| at most k different items | counter-dict, `len(counts)` |
| no repeats | counter-dict or set |
| count of zeros / vowels | one number |
| "has everything from t" | `need` dict plus `missing` number |

When a count hits 0, **delete the key** (`del counts[x]`). Otherwise `len(counts)` lies.

## Common mistakes

- Using sliding window with **negative numbers** for "sum at least / at most" questions. Shrinking only works when adding an item moves the sum in one direction (positive numbers). Negatives need prefix sums (a later lesson).
- Forgetting to **remove** the item at `lo` before `lo += 1`.
- Checking validity with `if` instead of `while`: one shrink step is often not enough.
- Not deleting a key whose count is 0, then trusting `len(counts)`.
- Off-by-one on length: it is `hi - lo + 1`.
- Updating the answer **before** the window is valid again.
- Moving `lo` backwards (for example `"abba"`): `lo` only ever moves right.

## Interview corner

**Q: How do you spot a sliding window question?**
A: A continuous subarray or substring, and a longest / shortest / count question with a condition on it.

**Q: Why is it O(n) when there is a `while` inside the `for`?**
A: `hi` moves right n times and `lo` moves right at most n times. Each pointer never goes back, so the total work is at most 2n.

**Q: Fixed or variable window?**
A: If the question gives the size `k`, fixed. If it asks for the longest or shortest part with a rule, variable.

**Q: When does sliding window fail?**
A: When the rule is not monotonic. With negative numbers, adding an item can make the sum smaller, so you cannot decide when to shrink. Use prefix sums and a dict instead.

**Q: How do you count subarrays with exactly k distinct?**
A: `at_most(k) - at_most(k - 1)`. The "at most" counter is exercise 17.

## Summary

- Sliding window: a range `[lo..hi]`, update by one item in, one item out. O(n).
- Fixed window: build the first, then add new and remove old.
- Variable maximum: shrink **while invalid**. Variable minimum: record **while valid**.
- Count: add `hi - lo + 1` for every `hi`.
- Store the smallest information that tells you if the window is valid.
- Only for continuous parts and monotonic rules (positive numbers for sums).
- Cheat sheet: `reference/patterns.md`. More revision: [Ep 14](https://www.youtube.com/watch?v=lyZp-49pdzQ) and [Ep 15](https://www.youtube.com/watch?v=IR3oL6ltbJ8).

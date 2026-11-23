# Longest subarray with sum at most k (positive numbers) vs any numbers

Write `longest_sum_at_most(nums, k)` for a list of **non-negative** integers: return the length of the longest contiguous subarray with sum `<= k` (`0` if none).

```python
longest_sum_at_most([1, 2, 1, 0, 1, 1, 0], 4)    # -> 5
longest_sum_at_most([5, 6], 4)                   # -> 0
```

**Think first:** because numbers are not negative, what happens to the sum when the window grows? When it shrinks?

**Hint:** pattern *sliding window (variable)*: add `right`; while the sum is `> k` remove `left`.

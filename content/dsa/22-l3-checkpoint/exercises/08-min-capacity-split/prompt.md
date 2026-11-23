# Split a list into at most m parts: smallest biggest sum

Write `min_largest_sum(nums, m)` that splits `nums` into **at most `m` contiguous parts** and returns the smallest possible value of the **largest part sum**. All numbers are positive.

```python
min_largest_sum([7, 2, 5, 10, 8], 2)    # -> 18    ([7, 2, 5] and [10, 8])
min_largest_sum([1, 2, 3], 5)           # -> 3
```

**Think first:** guess the biggest allowed part sum. Is it easy to check how many parts you need?

**Hint:** pattern *binary search on the answer*: range `max(nums)` to `sum(nums)`; greedy count of parts for a limit.

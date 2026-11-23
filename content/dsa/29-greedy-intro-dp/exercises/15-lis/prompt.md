# Longest increasing subsequence

A **subsequence** keeps the order but may skip items. Write `length_of_lis(nums)` that returns the length of the longest **strictly increasing** subsequence.

```python
length_of_lis([10, 9, 2, 5, 3, 7, 101, 18])    # -> 4    (2, 3, 7, 18)
length_of_lis([7, 7, 7])                       # -> 1
```

**Think first:** if `best[i]` is the longest increasing subsequence that **ends** at index `i`, how do you get it from earlier indexes?

**Hint:** pattern *DP on endings*: `best[i] = 1 + max(best[j])` for `j < i` with `nums[j] < nums[i]` (or `1` if none). Answer is `max(best)`.

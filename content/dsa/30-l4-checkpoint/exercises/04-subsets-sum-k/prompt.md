# Subsets with sum K

Write `subsets_with_sum(nums, k)` that returns every subset of `nums` (distinct positive numbers) that adds up to `k`. Each subset is a list in the **same order as `nums`**. Return the list of subsets **sorted**.

```python
subsets_with_sum([1, 2, 3, 4], 5)    # -> [[1, 4], [2, 3]]
subsets_with_sum([2, 4], 3)          # -> []
```

**Think first:** for each number you choose it or skip it. When can you stop early?

**Hint:** pattern *backtracking: choose / skip*: `go(i, path, total)`; stop when `total > k` (numbers are positive); save a copy when `total == k`.

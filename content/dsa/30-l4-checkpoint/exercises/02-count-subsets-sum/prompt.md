# Count subsets with a given sum

Write `count_subsets(nums, target)` that returns how many **subsets** (by position, so equal numbers at different positions count separately; the empty subset has sum 0) add up to `target`. Numbers are `>= 0`.

```python
count_subsets([1, 2, 3], 3)    # -> 2    ({3}, {1, 2})
count_subsets([0, 0], 0)       # -> 4
```

**Think first:** this is subset sum, but you count instead of answering yes or no.

**Hint:** pattern *knapsack DP (count)*: `ways[0] = 1`; for each number loop `s` from `target` down to `num`: `ways[s] += ways[s - num]`. Zeros need care: the downward loop still handles them if you include `s == 0`.

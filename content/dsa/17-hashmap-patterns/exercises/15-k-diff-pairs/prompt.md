# K-diff pairs

Write `k_diff_pairs(nums, k)` that counts the **unique pairs of values** `(a, b)` that are in `nums` at two different positions and have `abs(a - b) == k`. `k >= 0`. The pair `(1, 3)` and `(3, 1)` are the same pair.

```python
k_diff_pairs([3, 1, 4, 1, 5], 2)    # -> 2   ((1, 3) and (3, 5))
k_diff_pairs([1, 3, 1, 5, 4], 0)    # -> 1   ((1, 1))
```

**Think first:** for `k > 0`, for every value `x` what is the one partner to look for? For `k = 0`, what must be true about `x`?

**Hint:** pattern *counter-dict*: `k > 0`: count the values `x` where `x + k` is in the dict. `k = 0`: count values with count `>= 2`.

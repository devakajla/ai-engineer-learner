# 0/1 knapsack

`weights[i]` and `values[i]` describe item `i`. You have a bag that holds at most `capacity` weight, and each item can be used **once**. Write `knapsack(weights, values, capacity)` that returns the biggest total value.

```python
knapsack([1, 3, 4], [15, 20, 30], 4)    # -> 35
knapsack([5], [10], 4)                  # -> 0
```

**Think first:** for each item you take it or leave it. What must you remember about the remaining capacity?

**Hint:** pattern *knapsack DP*: `best[c]` = best value with capacity `c`; for each item loop `c` from `capacity` **down** to `weight` (so the item is used once): `best[c] = max(best[c], best[c - w] + v)`.

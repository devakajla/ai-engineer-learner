# Ship packages within D days

`weights[i]` is the weight of package `i`. Packages must be shipped **in the given order**; each day the ship carries some packages from the front, with a total weight at most `capacity`. Write `ship_capacity(weights, days)` that returns the **smallest capacity** that ships everything within `days` days.

```python
ship_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5)    # -> 15
ship_capacity([3, 2, 2, 4, 1, 4], 3)                 # -> 6
```

**Think first:** this is "allocate books" in disguise. What are the smallest and biggest possible capacities?

**Hint:** pattern *binary search on the answer*: `lo = max(weights)`, `hi = sum(weights)`; count days greedily for a capacity; if `days_needed <= days` try smaller.

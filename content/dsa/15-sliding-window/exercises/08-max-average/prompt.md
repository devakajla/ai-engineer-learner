# Maximum average of k in a row

Write `max_average(nums, k)` that returns the biggest **average** of any `k` consecutive numbers, as a float. `1 <= k <= len(nums)`.

```python
max_average([1, 12, -5, -6, 50, 3], 4)    # -> 12.75   ((12 - 5 - 6 + 50) / 4)
max_average([5], 1)                       # -> 5.0
```

**Think first:** is the biggest average the same window as the biggest sum?

**Hint:** pattern *fixed window*: slide the window sum like exercise 01, divide by `k` once at the end.

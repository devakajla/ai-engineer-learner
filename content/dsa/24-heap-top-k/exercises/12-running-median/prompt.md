# Running median

Numbers arrive one by one. Write `running_medians(nums)` that returns a list: the median of the numbers seen so far, after each new number. For an even count, the median is the **average** of the two middle numbers (a float is fine, e.g. `2.5`).

```python
running_medians([5, 15, 1, 3])    # -> [5, 10.0, 5, 4.0]
running_medians([2])              # -> [2]
```

**Think first:** the median splits the numbers into a small half and a big half. Which item of each half do you need to see?

**Hint:** pattern *two heaps*: a max-heap `low` (negatives) for the small half and a min-heap `high` for the big half; keep their sizes equal or `low` one bigger.

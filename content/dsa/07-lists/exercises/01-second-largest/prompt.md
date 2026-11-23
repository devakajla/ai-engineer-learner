# Second largest

Write `second_largest(nums)` that returns the second largest **distinct** value in a list. If there is none, return `None`.

```python
second_largest([3, 1, 4, 1, 5])   # -> 4
second_largest([7, 7, 7])         # -> None
second_largest([2])               # -> None
```

**Think first:** track two variables, `first` and `second`. What happens when a new biggest number arrives?

**Hint:** start both as `None`, update in one loop, skip numbers equal to `first`.

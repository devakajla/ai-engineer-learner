# First duplicate

Write `first_duplicate(nums)` that scans left to right and returns the first value that has **already appeared before**. Return `None` if all values are different.

```python
first_duplicate([2, 1, 3, 1, 2])    # -> 1    (the second 1 shows up before the second 2)
first_duplicate([1, 2, 3])          # -> None
```

**Think first:** why is "the second 1 comes first" the right answer, not "the first 2"?

**Hint:** a seen-set; return as soon as `x in seen`.

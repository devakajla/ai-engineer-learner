# Find all duplicates

Write `find_duplicates(nums)` that returns a **sorted** list of the values that appear **two or more times** (each value once in the result).

```python
find_duplicates([4, 3, 2, 7, 8, 2, 3, 1])    # -> [2, 3]
find_duplicates([1, 2, 3])                   # -> []
```

**Think first:** do you need the exact count, or only "have I seen it before"?

**Hint:** pattern *seen-set + repeated-set*: if `x` is in `seen`, put it in `repeated`; else add to `seen`. Return `sorted(repeated)`.

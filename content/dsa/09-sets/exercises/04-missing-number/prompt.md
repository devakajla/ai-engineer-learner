# Missing number

Write `missing_number(nums)` for a list that holds the numbers `0..n` with exactly one number missing (the list has length `n`). Return the missing number.

```python
missing_number([3, 0, 1])       # -> 2
missing_number([0, 1])          # -> 2
missing_number([1])             # -> 0
```

**Think first:** what should the complete set of numbers be?

**Hint:** compare `set(range(len(nums) + 1))` with `set(nums)`.

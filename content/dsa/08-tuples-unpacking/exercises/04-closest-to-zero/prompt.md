# Closest to zero

Write `closest_to_zero(nums)` for a non-empty list. Return the pair `(value, distance)` of the number closest to zero. If two numbers are equally close, return the positive one.

```python
closest_to_zero([4, -2, 7])     # -> (-2, 2)
closest_to_zero([-3, 3, 5])     # -> (3, 3)
closest_to_zero([0, 5])         # -> (0, 0)
```

**Think first:** "distance" is `abs(n)`. What decides a tie?

**Hint:** track `best` and compare `abs(n)`; on a tie prefer the larger value.

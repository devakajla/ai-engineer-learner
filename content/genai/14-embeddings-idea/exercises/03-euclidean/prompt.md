# Euclidean distance

Write `euclidean(a, b)`. It returns the straight-line distance between two vectors: the square root of the sum of the squared differences.

Rules:
- If the two lists have different lengths, raise `ValueError` with the message `"vectors must have the same length"`.
- Use `** 0.5` for the square root. Return a float.
- Two identical vectors have distance `0.0`.

```python
euclidean([0, 0], [3, 4])      # -> 5.0
euclidean([1, 2, 3], [1, 2, 3])  # -> 0.0
euclidean([1], [4])            # -> 3.0
```

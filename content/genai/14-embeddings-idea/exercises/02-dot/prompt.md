# Dot product

Write `dot(a, b)`. It multiplies the numbers of `a` and `b` in the same positions, and adds the results.

Rules:
- If the two lists have different lengths, raise `ValueError` with the message `"vectors must have the same length"`.
- Two empty lists give `0`.

```python
dot([1, 2, 3], [4, 5, 6])    # -> 32
dot([1, 0], [0, 1])          # -> 0
dot([], [])                  # -> 0
dot([1, 2], [1, 2, 3])       # raises ValueError
```

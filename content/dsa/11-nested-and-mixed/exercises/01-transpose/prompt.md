# Transpose a matrix

Write `transpose(matrix)` that returns the matrix with rows and columns swapped. The matrix is a non-empty rectangle (every row has the same length).

```python
transpose([[1, 2, 3], [4, 5, 6]])   # -> [[1, 4], [2, 5], [3, 6]]
transpose([[7]])                    # -> [[7]]
```

**Think first:** new row `c` is made of column `c` of the old matrix.

**Hint:** outer loop over columns, inner loop over rows.

# Row and column sums

Write `row_col_sums(matrix)` that returns a tuple `(row_sums, col_sums)`, both lists. The matrix is a non-empty rectangle.

```python
row_col_sums([[1, 2, 3], [4, 5, 6]])   # -> ([6, 15], [5, 7, 9])
```

**Think first:** row sums are easy. For columns, which index stays fixed?

**Hint:** `sum(row)` for rows; for columns add `row[c]` into a list of zeros.

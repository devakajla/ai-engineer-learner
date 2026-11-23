# Search in a matrix sorted by rows and columns

Every **row** is sorted ascending and every **column** is sorted ascending (but rows are **not** chained like in the previous exercise). Write `search_matrix_ii(matrix, target)` that returns `True` if `target` is in the matrix. Aim for O(rows + cols).

```python
m = [[1, 4, 7, 11], [2, 5, 8, 12], [3, 6, 9, 16], [10, 13, 14, 17]]
search_matrix_ii(m, 5)     # -> True
search_matrix_ii(m, 15)    # -> False
```

**Think first:** stand in the **top-right** corner. It is the biggest in its row and the smallest in its column. If it is too big, which column can you drop? If too small, which row?

**Hint:** pattern *staircase search*: `row, col = 0, cols - 1`; if the value is bigger than `target` then `col -= 1`; if smaller then `row += 1`.

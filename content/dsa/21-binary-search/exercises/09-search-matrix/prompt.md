# Search in a sorted matrix (flattened order)

`matrix` has rows; each row is sorted ascending and the **first number of a row is bigger than the last number of the row above**. So reading row by row gives one long sorted list. Write `search_matrix(matrix, target)` that returns `True` if `target` is in it. O(log(rows * cols)).

```python
m = [[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]]
search_matrix(m, 3)     # -> True
search_matrix(m, 13)    # -> False
```

**Think first:** you do not need to build the long list. How do you turn an index `i` of the long list into a row and a column?

**Hint:** pattern *binary search on a virtual list*: `lo = 0`, `hi = rows * cols - 1`; `row, col = divmod(mid, cols)`.

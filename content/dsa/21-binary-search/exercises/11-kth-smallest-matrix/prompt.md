# K-th smallest in a sorted matrix

`matrix` is `n x n`. Every row and every column is sorted ascending. Write `kth_smallest(matrix, k)` that returns the `k`-th smallest value (`k` starts at 1; equal values count separately). Do not sort everything.

```python
kth_smallest([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8)    # -> 13
kth_smallest([[-5]], 1)                                    # -> -5
```

**Think first:** guess a value `x`. Can you count how many matrix items are `<= x` in O(n) using the staircase walk from the previous exercise?

**Hint:** pattern *binary search on the answer (value range)*: `lo = matrix[0][0]`, `hi = matrix[-1][-1]`; `count_le(mid)`; if `count_le(mid) >= k` then `hi = mid`, else `lo = mid + 1`.

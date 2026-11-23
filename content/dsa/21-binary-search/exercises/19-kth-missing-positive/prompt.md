# K-th missing positive number

`arr` is sorted ascending with **unique positive** integers. The positive integers missing from `arr` are `1, 2, 3, ...` without the ones in `arr`. Write `kth_missing(arr, k)` that returns the `k`-th missing positive number (`k >= 1`).

```python
kth_missing([2, 3, 4, 7, 11], 5)    # -> 9    (missing: 1, 5, 6, 8, 9, ...)
kth_missing([1, 2, 3, 4], 2)        # -> 6
```

**Think first:** at index `i`, how many positive numbers are missing before `arr[i]`? (There should be `arr[i] - 1` numbers up to it, but `i` of them are present.)

**Hint:** pattern *binary search on a count*: `missing(i) = arr[i] - (i + 1)`. Find the first index where `missing(i) >= k`; the answer is `lo + k` (with `lo` that index).

# Peak of a mountain array

`arr` is a **mountain**: it goes strictly up, then strictly down, and has at least 3 items. Write `peak_index(arr)` that returns the index of the top. O(log n).

```python
peak_index([0, 2, 5, 3, 1])    # -> 2
peak_index([1, 3, 2])          # -> 1
```

**Think first:** at `mid`, compare `arr[mid]` with `arr[mid + 1]`. If it is still going up, where can the peak be?

**Hint:** pattern *binary search on a shape*: `if arr[mid] < arr[mid + 1]: lo = mid + 1 else: hi = mid`; loop `while lo < hi`.

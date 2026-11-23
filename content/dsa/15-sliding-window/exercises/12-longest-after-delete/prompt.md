# Longest run of 1s after deleting one item

`nums` holds only `0` and `1`. You **must delete exactly one item**. Write `longest_after_delete(nums)` that returns the length of the longest run of ones you can get after the deletion (`0` if none).

```python
longest_after_delete([1, 1, 0, 1])    # -> 3
longest_after_delete([1, 1, 1])       # -> 2   (you still have to delete one)
```

**Think first:** deleting one zero joins two runs. A window with at most one zero is what you want. Why is the answer `window length - 1`?

**Hint:** pattern *variable window, maximum* with "at most 1 zero"; the answer is the best `hi - lo` (the window minus the deleted item).

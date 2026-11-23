# First bad version

`flags` is a list of booleans like `[False, False, False, True, True]`: once it turns `True`, it stays `True`. Write `first_true(flags)` that returns the index of the first `True`, or `len(flags)` if there is none. Use binary search (imagine each lookup is expensive).

```python
first_true([False, False, True, True])    # -> 2
first_true([False, False])                # -> 2
```

**Think first:** this is the template behind many binary search questions: a yes/no check that flips once. What do you do when `flags[mid]` is `True`? Is `mid` the answer, or just a candidate?

**Hint:** pattern *first True template*: `lo, hi = 0, len(flags)`; `while lo < hi:` if `flags[mid]`: `hi = mid` else `lo = mid + 1`; return `lo`.

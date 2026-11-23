# Remove covered intervals

An interval `[a, b]` is **covered** by `[c, d]` if `c <= a` and `b <= d`. All intervals are different from each other. Write `remove_covered(intervals)` that returns **how many** intervals remain after removing the covered ones.

```python
remove_covered([[1, 4], [3, 6], [2, 8]])    # -> 2   ([3, 6] is covered by [2, 8])
remove_covered([[1, 4], [2, 3]])            # -> 1
```

**Think first:** if you sort by start (and by **bigger end first** when starts are equal), what must be true for an interval to be covered by an earlier one?

**Hint:** pattern *sort + running max end*: sort by `(start, -end)` (use `sorted((s, -e) ...)`); an interval is covered when its end is `<=` the biggest end seen so far.

# Can you finish all courses?

There are `n` courses `0 .. n-1`. Each pair `[a, b]` in `prereqs` means: you must take course `b` **before** course `a`. Write `can_finish(n, prereqs)` that returns `True` if you can take all courses.

```python
can_finish(2, [[1, 0]])            # -> True
can_finish(2, [[1, 0], [0, 1]])    # -> False
```

**Think first:** when is it impossible? Which node can you take first?

**Hint:** pattern *topological sort (Kahn)*: count `indegree` (number of prerequisites) per course; queue all with `0`; pop one, reduce the indegree of the courses that depend on it; if the number of courses taken is `n`, the answer is `True`.

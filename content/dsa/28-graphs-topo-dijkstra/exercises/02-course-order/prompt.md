# Order of courses

Same input as before. Write `find_order(n, prereqs)` that returns **one valid order** to take all courses (a list of course numbers), or `[]` if it is impossible. Any valid order is accepted.

```python
find_order(2, [[1, 0]])                            # -> [0, 1]
find_order(4, [[1, 0], [2, 0], [3, 1], [3, 2]])    # -> [0, 1, 2, 3] or [0, 2, 1, 3]
```

**Think first:** in Kahn's algorithm, in which order do courses leave the queue?

**Hint:** pattern *topological order*: append each course to `order` when you pop it; if `len(order) != n` there was a cycle, return `[]`.

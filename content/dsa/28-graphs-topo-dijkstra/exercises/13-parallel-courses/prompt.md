# Parallel courses: fewest semesters

There are `n` courses `1 .. n`. A pair `[a, b]` in `relations` means course `a` must be finished **before** course `b`. In one semester you may take **any number** of courses whose prerequisites are done in earlier semesters. Write `min_semesters(n, relations)` that returns the fewest semesters to take all courses, or `-1` if there is a cycle.

```python
min_semesters(3, [[1, 3], [2, 3]])    # -> 2
min_semesters(3, [[1, 2], [2, 3], [3, 1]])    # -> -1
```

**Think first:** which courses can go in semester 1? What can go in semester 2?

**Hint:** pattern *Kahn by levels*: process the queue **round by round** (`for _ in range(len(queue))`); each round is one semester; if you finish with fewer than `n` courses taken, return `-1`.

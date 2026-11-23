# Task scheduler

`tasks` is a list of letters; each task takes 1 unit of time. The same letter must have at least `n` units of **cooldown** between two runs (the CPU may stay idle). Write `least_interval(tasks, n)` that returns the least time needed to finish all tasks.

```python
least_interval(["A", "A", "A", "B", "B", "B"], 2)    # -> 8    (A B _ A B _ A B)
least_interval(["A", "A", "B"], 0)                   # -> 3
```

**Think first:** at each time step, which task should run: the one with the most copies left, or the one with the fewest?

**Hint:** pattern *max-heap + cooldown queue*: heap of `-count`; each step run the most frequent task; put it in a `deque` with the time it becomes free again; move it back to the heap when free.

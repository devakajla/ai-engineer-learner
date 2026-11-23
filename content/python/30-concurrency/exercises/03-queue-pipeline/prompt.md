# A worker pool with a queue

Write `pipeline(items, transform, workers=3)`:

- Start `workers` threads. Put the jobs in a `queue.Queue`. Each worker takes jobs and runs `transform(item)`.
- Return the results as a **list in the same order as `items`**.
- Stop the workers cleanly with one end marker (`None`) per worker. When `pipeline` returns, **all its threads must be finished**.
- If `workers < 1`, raise `ValueError`.
- `items` can be empty.

Do not use `ThreadPoolExecutor` here. Build it with `threading.Thread` and `queue.Queue`.

```python
pipeline([1, 2, 3, 4], lambda x: x * 10)       # -> [10, 20, 30, 40]
pipeline([], str)                              # -> []
```

**Think first:** How does a worker know which position its result belongs to? How does a worker know the work is over?

**Hint:** Put `(index, item)` in the queue. Each worker writes to its own `results[index]`. Put `None` in the queue once per worker, and `join()` every thread.

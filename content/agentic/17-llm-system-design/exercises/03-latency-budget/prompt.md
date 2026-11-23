# A latency budget

Users wait for the whole request. If your target is "an answer in under 1.5 seconds", every step spends part of that **budget**. Steps that depend on each other run **one after another** (their times add up). Steps that are independent can run **at the same time** (only the slowest one counts). The slowest chain is the **critical path**: the only place where saving time really makes the request faster.

Describe a pipeline as a list of **groups**. Groups run in order. Inside a group, the items run in parallel. An item is `(name, milliseconds)`:

```python
stages = [
    [("auth", 20)],
    [("vector_search", 80), ("keyword_search", 50)],   # in parallel
    [("llm", 900)],
]
```

Write:

1. `total_latency(stages)`: the sum over the groups of the **slowest item** in each group (an empty group counts as 0).
2. `critical_path(stages)`: the list of the slowest `(name, ms)` item of each non-empty group, in order (on a tie keep the first).
3. `latency_report(stages, budget_ms)`: return `{"total_ms": ..., "ok": total <= budget_ms, "over_by": max(0, total - budget_ms), "biggest": <name of the slowest item on the critical path, or None if the path is empty>}`.

```python
latency_report(stages, 1000)
# -> {'total_ms': 1000, 'ok': True, 'over_by': 0, 'biggest': 'llm'}
```

**Think first:** your pipeline is over budget by 200 ms and the biggest item is the model call. Name two ways to win time without touching the model.

**Hint:** `max(group, key=lambda item: item[1])` gives the slowest item. (A `lambda` is a tiny function. Python lesson 25 explains it. Or write a normal loop.)

# Choose with numbers, not feelings

You measured three ways to do the same task on your test questions. Now pick one.

Write `pick_by_numbers(candidates, min_success, max_cost, max_seconds)`.

- `candidates` is a list of dictionaries: `{"name": ..., "success": ..., "cost": ..., "seconds": ...}`. `success` is the share of test questions answered right (`0` to `1`). `cost` is dollars per question. `seconds` is the average time.
- A candidate is **good enough** when `success >= min_success`, `cost <= max_cost` **and** `seconds <= max_seconds`. (At the limit is still good.)
- Return the **name** of the cheapest good candidate. If two cost the same, the faster one wins. If they are still equal, the name that comes first in the alphabet wins.
- If no candidate is good enough, return `None`.

```python
options = [
    {"name": "single", "success": 0.70, "cost": 0.001, "seconds": 1},
    {"name": "workflow", "success": 0.90, "cost": 0.004, "seconds": 4},
    {"name": "agent", "success": 0.95, "cost": 0.030, "seconds": 20},
]
pick_by_numbers(options, 0.85, 0.05, 30)   # -> 'workflow'
pick_by_numbers(options, 0.99, 0.05, 30)   # -> None
```

**Think first:** the agent has the best success. Why is it not chosen above? What would you change to get it chosen?

**Hint:** first make a list of the good candidates. Then use `min(good, key=rank)`, where `rank` is a small function that returns a tuple `(cost, seconds, name)`. Tuples compare from left to right.

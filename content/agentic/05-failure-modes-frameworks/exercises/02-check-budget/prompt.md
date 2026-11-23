# Stop an agent that spends too much

Every agent needs a **budget**: limits on steps, tokens, money and time. Check the budget before each step, and stop when a limit is reached.

Write `check_budget(used, limits)`.

- `used` is a dictionary with any of the keys `steps`, `tokens`, `cost`, `seconds` (a missing key counts as 0).
- `limits` is a dictionary with any of the keys `max_steps`, `max_tokens`, `max_cost`, `max_seconds`. A limit that is **missing** is not checked.
- A limit is reached when `used >= limit`.
- Check in this order: `max_steps` (compared with `steps`), `max_tokens` (`tokens`), `max_cost` (`cost`), `max_seconds` (`seconds`).
- Return the name of the **first** limit that is reached, for example `"max_tokens"`. If none is reached, return `None`.

```python
check_budget({"steps": 3, "tokens": 900}, {"max_steps": 5, "max_tokens": 1000})   # -> None
check_budget({"steps": 5, "tokens": 900}, {"max_steps": 5, "max_tokens": 1000})   # -> 'max_steps'
check_budget({"cost": 0.5}, {})                                                    # -> None
```

**Think first:** why `>=` and not `>`? What happens to a run that has used exactly its limit?

**Hint:** a list of `(limit_name, used_name)` pairs and a `for` loop keeps the code short. `used.get("steps", 0)` gives 0 when the key is missing.

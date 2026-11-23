# How errors pile up

Every step of an agent can go wrong. If each step is right 95% of the time, the whole run is **not** right 95% of the time. The chances multiply.

Write `chain_success(step_success, steps)`.

- `step_success` is the chance that one step works, from `0` to `1`.
- `steps` is how many steps in a row must all work.
- Return the chance that **all** steps work: `step_success` multiplied by itself `steps` times, rounded to 4 decimals with `round(x, 4)`.
- With `steps` of `0` or less, nothing can fail: return `1.0`.
- If `step_success` is below `0` or above `1`, raise `ValueError`.

```python
chain_success(0.95, 10)   # -> 0.5987
chain_success(0.99, 5)    # -> 0.951
chain_success(0.9, 0)     # -> 1.0
```

**Think first:** a workflow with 3 steps at 0.95 and an agent that needs 12 steps at 0.95. Which one do you trust more? Why?

**Hint:** the power operator is `**`.

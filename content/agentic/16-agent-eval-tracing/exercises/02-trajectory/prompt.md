# Did it take the right path?

An agent can give the right answer by a bad road (ten tool calls where two were enough, or luck instead of the right tool). So you also check the **trajectory**: the list of tools it called. You compare it with the list you **expected**.

Write:

1. `tool_names(trace)`: the `name` of every span whose `kind` is `"tool"`, in order.
2. `trajectory_match(actual, expected, mode="exact")`, with three modes:
   - `"exact"`: the two lists are equal.
   - `"in_order"`: every expected tool appears in `actual`, **in that order**, extra steps in between are fine. (A trick: `remaining = iter(actual)` and `all(name in remaining for name in expected)`. Using `in` on an iterator uses it up as it goes. Think about why this checks the order.)
   - `"any_order"`: every expected tool appears somewhere in `actual`.
   - Any other mode raises `ValueError(f"unknown mode: {mode}")`.
3. `step_efficiency(actual, expected)`: `len(expected) / len(actual)`, never above `1.0`, rounded to 2 decimals. If `actual` is empty: `1.0` when `expected` is empty too, otherwise `0.0`.

```python
trajectory_match(["search", "log", "calc"], ["search", "calc"], "in_order")
# -> True
step_efficiency(["a", "b", "c", "d"], ["a", "b"])
# -> 0.5
```

**Think first:** which mode would you pick for an agent where the order of two tools does not matter, and which where it does?

**Hint:** `in` on a list checks anywhere. `in` on an iterator checks only what is still ahead.

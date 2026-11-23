# A gate for changes

Every change to a prompt, a model or a tool can make the agent better on some cases and **worse on others**. Run the eval before and after, and **block the change** if it got worse. This is a **regression gate**. You can run it in CI before every release.

The starter gives you `run_eval` and `pass_rate` (exercise 3). A result is a dict with `id`, `passed` and `tokens`. Write:

1. `find_regressions(baseline, new)`: the ids (in the order of `new`) of cases that **passed in the baseline and fail now**. Cases that failed before, or are new, are not regressions.
2. `gate(baseline, new, max_drop=0.05, max_token_growth=0.2)`: collect `reasons` (strings), in this order:
   - let `drop = round(pass_rate(baseline) - pass_rate(new), 2)` (rounding avoids float noise like `0.0500000001`). If `drop > max_drop`: `f"pass rate fell by {drop}"`.
   - if there are regressions: `"regressions: " + ", ".join(ids)`.
   - if the baseline used some tokens (the sum of `tokens` is above 0) and the total tokens of `new` grew by more than `max_token_growth` (as a fraction of the baseline): `f"token use grew by {round(100 * growth)}%"`.
   Return `{"ok": not reasons, "reasons": reasons}`.

```python
gate(baseline, new)
# -> {'ok': False, 'reasons': ['pass rate fell by 0.5', 'regressions: a, b']}
```

**Think first:** why block on **one** regression even when the overall pass rate stayed the same?

**Hint:** build a dict `before = {id: passed}` first, then loop over `new`.

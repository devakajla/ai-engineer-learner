# Design drill 3: is the service healthy?

**Asked as:** "What would you monitor, and when would you page someone?"

For an LLM service, two numbers come first: **p95 latency** (the time that 95% of requests beat) and the **error rate**. You compare them with your targets (an **SLA** or **SLO**) and report what is wrong.

The starter gives you `percentile(values, p)` (nearest rank, from lesson 18). Write `sla_status(latencies_ms, errors, total, p95_limit_ms, max_error_rate)`:

- `p95 = percentile(latencies_ms, 95)`.
- `error_rate = round(errors / total, 4)` (`0.0` if `total` is `0`).
- `problems` is a list: add `"latency"` if `p95 > p95_limit_ms`, then add `"errors"` if `error_rate > max_error_rate` (in this order).
- Return `{"p95_ms": p95, "error_rate": error_rate, "ok": <no problems>, "problems": problems}`.

```python
sla_status([3000] * 10, errors=50, total=100, p95_limit_ms=1000, max_error_rate=0.1)
# -> {'p95_ms': 3000, 'error_rate': 0.5, 'ok': False, 'problems': ['latency', 'errors']}
```

**Think first:** which other numbers would you watch for an LLM app? (Cost per request, tokens, cache hit rate, the share of "I don't know" answers, the rate of step-limit hits.)

**Hint:** being exactly on a limit is fine. Only values **above** the limit are a problem.

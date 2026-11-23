# A dashboard in one function

You cannot improve what you cannot see. If you log every model call, one function can turn the log into the numbers that matter: error rate, cost and speed.

In the starter: `estimate_cost` (Level 1) and `import math`. Write `summarize_calls(calls, prices)`.

- `calls`: a list of dictionaries `{"model", "input", "output", "ms", "ok"}`: tokens in, tokens out, time in milliseconds, and `ok` (False for an error).
- `prices`: `{model: (input_price, output_price)}`, prices per million tokens.

Return a dictionary:
- `"n"`: number of calls.
- `"errors"`: number of calls with `ok` false. `"error_rate"`: `errors / n`, rounded to 4 decimals.
- `"total_cost"`: the sum of `estimate_cost(input, output, input_price, output_price)` for all calls whose model is in `prices`, rounded to 6 decimals.
- `"unpriced"`: number of calls whose model is **not** in `prices` (they add 0 to the cost, but you must see how many).
- `"avg_ms"`: the average time, rounded to 1 decimal.
- `"p95_ms"`: the 95th percentile of the times: sort the times, and take the item at index `math.ceil(0.95 * n) - 1`. "95% of calls were this fast or faster."

With no calls return `{"n": 0, "errors": 0, "error_rate": 0.0, "total_cost": 0.0, "avg_ms": 0.0, "p95_ms": 0, "unpriced": 0}`.

```python
calls = [{"model": "m", "input": 1000, "output": 500, "ms": 800, "ok": True},
         {"model": "m", "input": 2000, "output": 0, "ms": 2000, "ok": False}]
summarize_calls(calls, {"m": (1.0, 2.0)})
# -> {'n': 2, 'errors': 1, 'error_rate': 0.5, 'total_cost': 0.004, 'avg_ms': 1400.0, 'p95_ms': 2000, 'unpriced': 0}
```

**Think first:** why look at p95 and not only the average?

# Capstone part 3: the report you show an interviewer

A capstone is only convincing with **numbers**. After running your eval set (lesson 16) you want one short report: how many cases, the pass rate, the average number of steps, total tokens, the **p95 latency**, and which cases failed.

The starter gives you `import math` and `pass_rate(results)` (lesson 16). A result is `{"id", "passed", "steps", "tokens", "ms"}`. Write:

1. `percentile(values, p)`: the **nearest-rank** percentile. Sort the values, `rank = math.ceil(p / 100 * len(values))`, return `ordered[max(rank, 1) - 1]`. An empty list gives `0`.
2. `capstone_report(results)`: return a dict with `cases` (count), `pass_rate` (from `pass_rate`), `avg_steps` (the mean of `steps`, rounded to 2 decimals, `0.0` if there are no results), `total_tokens` (sum), `p95_ms` (`percentile` of the `ms` values with `p = 95`) and `failed` (the ids of results that did not pass, in order).
3. `format_report(report)`: a text of 6 lines joined with `"\n"`:
   ```
   Cases: 4
   Pass rate: 75%
   Average steps: 3.0
   Total tokens: 1000
   p95 latency: 3000 ms
   Failed: b, e
   ```
   The pass rate is shown as a whole percent (use the format `f"{rate:.0%}"`). If nothing failed the last line is `Failed: none`.

```python
format_report(capstone_report(results)).splitlines()[1]
# -> 'Pass rate: 75%'
```

**Think first:** why show p95 latency and not only the average?

**Hint:** the average hides the slow requests that users remember. p95 shows them.

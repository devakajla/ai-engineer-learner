# Stock span

`prices[i]` is the price on day `i`. Write `stock_spans(prices)` that returns, for each day, the **span**: how many days in a row (going back, including today) the price was **less than or equal** to today's price.

```python
stock_spans([100, 80, 60, 70, 60, 75, 85])    # -> [1, 1, 1, 2, 1, 4, 6]
stock_spans([10, 10, 10])                     # -> [1, 2, 3]
```

**Think first:** if yesterday's span already covers some days, can you jump over them at once?

**Hint:** pattern *monotonic stack of indexes*: pop while `prices[stack[-1]] <= price`; span is `i - stack[-1]` (or `i + 1` if the stack is empty).

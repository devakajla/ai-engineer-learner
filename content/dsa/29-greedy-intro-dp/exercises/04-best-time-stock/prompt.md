# Buy and sell stock many times

`prices[i]` is the price on day `i`. You may buy and sell as many times as you like, but you hold at most one share at a time. Write `max_profit(prices)` that returns the biggest total profit.

```python
max_profit([7, 1, 5, 3, 6, 4])    # -> 7
max_profit([5, 4, 3])             # -> 0
```

**Think first:** every rise from one day to the next can be collected separately.

**Hint:** pattern *greedy: take every gain*: add `prices[i] - prices[i-1]` whenever it is positive.

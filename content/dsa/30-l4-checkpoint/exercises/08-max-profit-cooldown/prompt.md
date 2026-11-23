# Stock with one day of rest

`prices[i]` is the price on day `i`. You may buy and sell many times, but after you **sell**, you must rest one day before buying again. You hold at most one share. Write `max_profit_cooldown(prices)`.

```python
max_profit_cooldown([1, 2, 3, 0, 2])    # -> 3
max_profit_cooldown([1])                # -> 0
```

**Think first:** on each day what states can you be in?

**Hint:** pattern *state DP*: keep `hold` (own a share), `sold` (just sold today), `rest` (free and able to buy). Update all three each day from yesterday's values.

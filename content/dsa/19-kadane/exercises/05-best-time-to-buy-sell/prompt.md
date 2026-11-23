# Best time to buy and sell (one trade)

`prices[i]` is the price on day `i`. You may buy once and sell **later** once. Write `max_profit(prices)` that returns the biggest profit, or `0` if you cannot make any.

```python
max_profit([7, 1, 5, 3, 6, 4])    # -> 5    (buy at 1, sell at 6)
max_profit([7, 6, 4, 3, 1])       # -> 0
```

**Think first:** to sell today at the best profit, which earlier day would you have bought on?

**Hint:** pattern *running minimum* (Kadane on price changes): keep the lowest price so far, `profit = price - lowest`, track the best.

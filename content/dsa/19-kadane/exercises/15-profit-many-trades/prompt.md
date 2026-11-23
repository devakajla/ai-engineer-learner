# Best time to buy and sell (many trades)

`prices[i]` is the price on day `i`. You may buy and sell as many times as you like, but you hold **at most one share** at a time. Write `max_profit_many(prices)` that returns the biggest total profit.

```python
max_profit_many([7, 1, 5, 3, 6, 4])    # -> 7    (1 -> 5 and 3 -> 6)
max_profit_many([1, 2, 3, 4, 5])       # -> 4
```

**Think first:** a long climb is the same as the sum of its daily rises. Which daily changes should you collect?

**Hint:** pattern *collect every rise*: add `prices[i] - prices[i - 1]` whenever it is positive.

# Coin change: number of ways

Same coins (unlimited). Write `coin_ways(coins, amount)` that returns **how many different combinations** make `amount` (order does not matter: `1+2` and `2+1` count once).

```python
coin_ways([1, 2, 5], 5)    # -> 4
coin_ways([2], 3)          # -> 0
```

**Think first:** how do you stop `1+2` and `2+1` from being counted twice?

**Hint:** pattern *DP with coin loop outside*: `ways = [1] + [0] * amount`; for each coin, for `a` from `coin` to `amount`: `ways[a] += ways[a - coin]`.

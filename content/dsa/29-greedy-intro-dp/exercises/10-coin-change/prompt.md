# Coin change: fewest coins

`coins` are coin values (unlimited supply of each). Write `coin_change(coins, amount)` that returns the **fewest coins** that make `amount`, or `-1` if impossible.

```python
coin_change([1, 2, 5], 11)    # -> 3    (5+5+1)
coin_change([2], 3)           # -> -1
```

**Think first:** why does "always take the biggest coin" fail for `[1, 3, 4]` and `6`?

**Hint:** pattern *1D DP over amounts*: `best[a] = 1 + min(best[a - c])` over coins `c <= a`; `best[0] = 0`.

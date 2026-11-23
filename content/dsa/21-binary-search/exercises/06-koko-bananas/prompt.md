# Koko eating bananas

`piles[i]` is the number of bananas in pile `i`. Koko eats at speed `k` bananas per hour: each hour she picks **one pile** and eats up to `k` from it (if the pile has fewer, she finishes it and waits for the next hour). She must finish all piles within `h` hours (`h >= len(piles)`). Write `min_eating_speed(piles, h)` that returns the smallest `k` that works.

```python
min_eating_speed([3, 6, 7, 11], 8)           # -> 4
min_eating_speed([30, 11, 23, 4, 20], 5)     # -> 30
```

**Think first:** if speed `k` works, does `k + 1` work too? That "yes/no flips once" idea means you can binary search the **answer** itself.

**Hint:** pattern *binary search on the answer*: search `k` from `1` to `max(piles)`. `hours(k) = sum((p + k - 1) // k for p in piles)` (ceiling). If `hours <= h` try smaller (`hi = mid`), else `lo = mid + 1`.

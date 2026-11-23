# Cheapest flights with at most K stops

`flights` has directed edges `[u, v, price]`. Write `cheapest_price(n, flights, src, dst, k)` that returns the cheapest price from `src` to `dst` using **at most `k` stops** (so at most `k + 1` flights), or `-1` if impossible.

```python
cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 1)    # -> 200
cheapest_price(3, [[0, 1, 100], [1, 2, 100], [0, 2, 500]], 0, 2, 0)    # -> 500
```

**Think first:** plain Dijkstra may pick a cheap path with too many stops. What extra limit must the search respect?

**Hint:** pattern *Bellman-Ford with a round limit*: repeat `k + 1` times: from a **copy** of the previous distances relax every edge. The copy stops you from using two flights in one round.

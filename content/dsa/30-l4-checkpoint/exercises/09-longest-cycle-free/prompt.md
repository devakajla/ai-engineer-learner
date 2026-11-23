# Largest group of friends

`friends` is a list of pairs `[a, b]` (people are `0 .. n-1`, friendship works both ways). Write `largest_group(n, friends)` that returns the size of the biggest group of people connected directly or through other friends.

```python
largest_group(5, [[0, 1], [1, 2], [3, 4]])    # -> 3
largest_group(3, [])                          # -> 1
```

**Think first:** this is "count components" with a twist: you want the biggest size.

**Hint:** pattern *components with sizes*: DFS from each unvisited person, count how many you reach, keep the max. Return `0` when `n == 0`.

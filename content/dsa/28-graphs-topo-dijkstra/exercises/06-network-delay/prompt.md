# Network delay time

Nodes are numbered `1 .. n`. `times` has directed edges `[u, v, w]`: a signal from `u` reaches `v` after `w` time units. A signal starts at node `k`. Write `network_delay(times, n, k)` that returns the time until **all** nodes have the signal, or `-1` if some node is never reached.

```python
network_delay([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)    # -> 2
network_delay([[1, 2, 1]], 2, 2)                          # -> -1
```

**Think first:** a signal moves along every path at once. How long until the **last** node hears it?

**Hint:** pattern *Dijkstra, then take the max*: shortest time to each node; the answer is the biggest of them (or `-1` if any is infinite).

# BFS visit order

Same input as DFS. Write `bfs_order(graph, start)` that returns the nodes reachable from `start` in **breadth-first** order (first all neighbours, then neighbours of neighbours). Visit neighbours in the listed order.

```python
g = {0: [1, 2], 1: [0, 3], 2: [0], 3: [1]}
bfs_order(g, 0)    # -> [0, 1, 2, 3]
```

**Think first:** which structure gives first in, first out? When should you mark a node as visited: when you take it out, or when you put it in?

**Hint:** pattern *BFS with a queue*: `from collections import deque`; mark visited **when you push**, so a node enters the queue only once.

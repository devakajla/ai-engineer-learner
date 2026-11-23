---
title: "Graphs: Topological Sort, Dijkstra & More"
summary: "Order tasks with dependencies, colour graphs in two, and find cheapest paths with a heap."
plan_ids: []
---

Level 3 graph search treats every edge the same. Now edges get **direction** (dependencies) and **weights** (costs). This lesson covers ordering, two-colouring, shortest paths with weights, and spanning trees.

> Watch the intro video first. You need `heapq` and `deque` from `reference/heap-and-deque.md`.

## Topological sort (Kahn's algorithm)

A directed graph without cycles can be put in a line so every arrow points forward. Use it for "course A needs course B first".

1. Count `indegree[node]`: how many arrows point **into** it.
2. Queue every node with indegree `0` (nothing blocks it).
3. Pop a node, add it to the order, and lower the indegree of the nodes it points to. When one reaches `0`, queue it.
4. If the order has fewer than `n` nodes, there is a cycle.

```python
from collections import deque

def topo(n, edges):          # edge [a, b]: a before b
    graph = {i: [] for i in range(n)}
    indegree = [0] * n
    for a, b in edges:
        graph[a].append(b)
        indegree[b] += 1
    queue = deque(i for i in range(n) if indegree[i] == 0)
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for nb in graph[node]:
            indegree[nb] -= 1
            if indegree[nb] == 0:
                queue.append(nb)
    return order

print(topo(3, [[0, 1], [1, 2]]))   # -> [0, 1, 2]
```

Process the queue in rounds to count levels (semesters).

## Bipartite check (two colours)

Colour a node, give its neighbours the other colour, keep spreading. If a neighbour already has the same colour as you, the answer is `False`. Run it from every uncoloured node, because the graph may be disconnected.

## Dijkstra: shortest path with weights

BFS counts edges. With weights, use a **min-heap** of `(distance, node)`. The smallest popped distance is final, as long as no weight is negative.

```python
import heapq

def dijkstra(n, edges, src):         # edge [u, v, w], directed
    graph = {i: [] for i in range(n)}
    for u, v, w in edges:
        graph[u].append((v, w))
    dist = [float("inf")] * n
    dist[src] = 0
    heap = [(0, src)]
    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]:
            continue                 # stale entry
        for nb, w in graph[node]:
            if d + w < dist[nb]:
                dist[nb] = d + w
                heapq.heappush(heap, (dist[nb], nb))
    return dist

print(dijkstra(3, [[0, 1, 4], [0, 2, 1], [2, 1, 2]], 0))   # -> [0, 3, 1]
```

The same shape solves variants: cost = **max** along the path (swim in water, min effort), or **product** (probability: push the negative), or a **counter** of equal-cost paths.

## Bellman-Ford: negative weights

Relax every edge `n - 1` times. If an edge can still improve after that, a negative cycle exists. Slower than Dijkstra (O(V * E)), but handles negative edges. Limit the rounds to `k + 1` (using a copy of the distances each round) for "at most k stops".

## Minimum spanning tree (Prim)

Connect all nodes with the smallest total weight and no cycle. Start from one node, keep a heap of edges leaving the tree, always take the cheapest one that reaches a new node.

## Word ladder: an implicit graph

You do not always get edges. Words are nodes; neighbours differ by one letter. Generate neighbours on the fly and run BFS.

## Common mistakes

- Dijkstra with negative weights (use Bellman-Ford).
- Forgetting the `if d > dist[node]: continue` check (works, but slower).
- Kahn: forgetting to compare the order length with `n` (cycle missed).
- Bipartite: starting from node 0 only; disconnected parts are skipped.
- Bellman-Ford with k limit: updating `dist` in place lets one round use many flights.
- Edge direction reversed in prerequisites (`[a, b]` means b first).

## Interview corner

**Q: When can you not use Dijkstra?**
A: With negative edge weights. Use Bellman-Ford.

**Q: How do you detect a cycle with Kahn's algorithm?**
A: If fewer than `n` nodes come out of the queue, the rest are in a cycle.

**Q: Dijkstra complexity?**
A: O((V + E) log V) with a heap.

**Q: BFS or Dijkstra?**
A: BFS when every edge costs the same; Dijkstra when weights differ.

## Summary

- Dependencies: Kahn's topological sort (indegree + queue).
- Two groups: bipartite colouring.
- Weighted shortest path: Dijkstra with a heap; negative weights: Bellman-Ford.
- Cheapest connection of everything: Prim (minimum spanning tree).
- Cheat sheet: `reference/patterns.md`, tools: `reference/heap-and-deque.md`.

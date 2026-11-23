---
title: "Graphs: BFS & DFS"
summary: "Model connections as a graph, then explore with DFS (go deep) or BFS (go in rings) and a visited set."
plan_ids: []
---

A **graph** is nodes (things) and edges (connections): cities and roads, people and friendships, cells in a grid. Many problems are graph problems in disguise, especially grids.

> Watch the intro video first. Exercises 01 to 11 have video segments. New tool: `deque`, see `reference/heap-and-deque.md`.

## Words

- **Undirected edge:** works both ways. **Directed edge:** one way (an arrow).
- **Neighbours** of a node: nodes it connects to.
- **Connected component:** a group of nodes that can reach each other.
- **Cycle:** you can leave a node and come back to it.

## Representing a graph

Use an **adjacency list**: a dict from node to its neighbours.

```python
n = 3
edges = [[0, 1], [1, 2]]
graph = {i: [] for i in range(n)}
for a, b in edges:
    graph[a].append(b)
    graph[b].append(a)      # remove this line for a directed graph
print(graph)   # -> {0: [1], 1: [0, 2], 2: [1]}
```

An adjacency matrix (`m[i][j] == 1`) is simple but uses n * n space. A grid needs no building at all: the neighbours of `(r, c)` are `(r+1, c)`, `(r-1, c)`, `(r, c+1)`, `(r, c-1)`.

## Always: a visited set

A graph can have cycles. Without a `visited` set you walk in circles forever. Mark a node visited **when you put it in the stack or queue**, not later.

## DFS: go deep first

```python
def dfs_order(graph, start):
    visited, order = set(), []

    def visit(node):
        visited.add(node)
        order.append(node)
        for nb in graph[node]:
            if nb not in visited:
                visit(nb)

    visit(start)
    return order
```

Use DFS to explore a whole component, count components, flood fill, detect cycles, or enumerate paths.

## BFS: go in rings

```python
from collections import deque

def bfs_order(graph, start):
    visited, order = {start}, []
    queue = deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return order
```

BFS reaches nodes in order of distance, so it finds the **shortest path when every step costs the same**. Process the queue by rounds (`for _ in range(len(queue))`) to count levels or minutes.

## Pattern: count components

Loop over all nodes; every time you meet an unvisited node, `count += 1` and explore its whole component. Islands = components on a grid.

## Pattern: multi-source BFS

Put **all** starting cells in the queue at the start (all rotten oranges, all zeros). They spread at the same speed, so each round is one time step.

## Pattern: cycle detection

- **Undirected:** DFS with a `parent`. Meeting a visited node that is not the parent means a cycle.
- **Directed:** three states: new, on the current path, finished. Meeting a node on the current path means a cycle.

## Pattern: start from the border

For "surrounded regions", find what is **not** captured by flooding from the border cells.

## Common mistakes

- No `visited` set: infinite loop.
- Marking visited too late (when popping), so nodes enter the queue many times.
- Mutating the input grid when you should return a new one.
- Wrong neighbour bounds (`0 <= r < rows`).
- Using DFS for shortest path.
- Treating undirected edges as one direction (add both).

## Interview corner

**Q: DFS vs BFS?**
A: DFS goes deep and fits components, cycles and paths. BFS goes ring by ring and finds shortest paths in unweighted graphs.

**Q: Time complexity?**
A: O(V + E) for a list, O(rows * cols) for a grid.

**Q: Why mark visited when pushing in BFS?**
A: Otherwise the same node can be queued many times by different neighbours.

**Q: How do you detect a cycle in a directed graph?**
A: DFS with states: a node on the current path that you reach again is a cycle.

## Summary

- Graph = adjacency list (or grid neighbours) + `visited`.
- DFS for components and cycles; BFS for shortest steps and rounds; multi-source BFS spreads from many starts.
- Cheat sheet: `reference/patterns.md`.

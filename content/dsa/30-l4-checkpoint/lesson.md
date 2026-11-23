---
title: "Level 4 checkpoint"
summary: "Mixed revision: pick the right pattern for each problem from Level 4."
plan_ids: []
---

Level 4 added linked lists, heaps, backtracking, trees, graphs, greedy and DP. This checkpoint mixes them. For each problem, **name the pattern first**, then code.

## Pattern chooser

| You see | Try |
| --- | --- |
| Middle, cycle, k-th from end on a list | Slow/fast pointers, reversal |
| Top k, k-th largest, merge sorted streams, "always the smallest" | Heap (`heapq`) |
| "All subsets, permutations, combinations, placements" | Backtracking: choose, explore, undo |
| Hierarchy, depth, ancestors, sorted order of a BST | Tree recursion or BFS levels |
| Groups, islands, reachability, "fewest steps" with equal cost | Graph DFS/BFS, visited set |
| Rounds from many starts at once | Multi-source BFS |
| Dependencies, ordering, cycle in arrows | Topological sort (Kahn) |
| Cheapest path with weights | Dijkstra (heap); negative weights: Bellman-Ford |
| Connect everything cheaply | Minimum spanning tree (Prim) |
| Best local choice stays best after sorting | Greedy (test with a counter-example) |
| Max, min, count of ways from overlapping sub-answers | DP: state, transition, base case, answer |

## How to use this level

1. Read the problem. Write the pattern name before coding.
2. If two patterns fit (greedy or DP?), try a tiny counter-example for greedy first.
3. For DP, write what `dp[i]` means in one sentence before any code.
4. When the tests fail, find which edge case broke it: empty input, one item, no path, a cycle.

## Common mistakes

- Greedy where a counter-example exists (coin change).
- Forgetting a `visited` set in graph search.
- Using Dijkstra with negative weights.
- Plain recursion on overlapping sub-problems (no DP).
- Not copying the path when saving a backtracking result.

## Interview corner

**Q: How do you tell greedy from DP?**
A: Greedy commits to one local choice. If a counter-example shows that choice can fail, you need DP, which tries all choices and remembers results.

**Q: BFS or Dijkstra?**
A: BFS when every step costs the same, Dijkstra when costs differ and are not negative.

**Q: When do you reach for a heap?**
A: When you repeatedly need the smallest or largest item from a changing set, or the top k.

**Q: Which patterns share the same shape?**
A: Subset sum and knapsack (boolean vs value), swim in water and min effort (Dijkstra with max), course order and alien order (topological sort).

## Summary

- Name the pattern first, then code.
- Cheat sheet: `reference/patterns.md`; tools: `reference/heap-and-deque.md`.

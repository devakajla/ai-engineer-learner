# Sort with a heap

A heap gives you the smallest item fast. Write `heap_sort(nums)` that returns a new sorted list (ascending) by pushing all numbers into a heap and popping them one by one. Use `heapq` (see `reference/heap-and-deque.md`). Do not call `sorted` or `.sort()`.

```python
heap_sort([5, 1, 4, 2])    # -> [1, 2, 4, 5]
heap_sort([])              # -> []
```

**Think first:** what comes out of a min-heap on every `heappop`?

**Hint:** pattern *push all, pop all*: `heapq.heappush(h, x)` for each number, then `heapq.heappop(h)` `len(nums)` times.

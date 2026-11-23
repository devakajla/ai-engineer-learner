---
title: "Heap & top-K"
summary: "Use a heap to always get the smallest (or biggest) item fast: top-K, merging, scheduling and medians."
plan_ids: []
---

A **heap** is a list arranged so the **smallest** item is always at index 0. Getting it costs O(1). Adding or removing costs O(log n). Sorting everything costs O(n log n), so when you only need the best few, a heap wins.

> Python's `heapq` is new here. Full entry: `reference/heap-and-deque.md`. Watch the intro video first.

## `heapq` in 30 seconds

```python
import heapq

h = []
heapq.heappush(h, 5)
heapq.heappush(h, 1)
heapq.heappush(h, 4)
print(heapq.heappop(h))   # -> 1  (smallest comes out first)
print(h[0])               # -> 4  (peek)
```

- It is a **min-heap**. For a max-heap push the negative: `heappush(h, -x)`, and `-heappop(h)`.
- To order by several things, push a **tuple**: `(-count, word)`. Python compares the first item, then the second.
- Only change `h` with `heapq` functions. Never `h.sort()` or `h.append()`.
- `heapq.heapify(list)` makes a heap in O(n).

## When to think "heap"

- "k largest", "k smallest", "k most frequent", "k closest".
- "Always take the best next item" (greedy), while new items keep arriving.
- Merge many sorted sources.
- Median of a stream.

## Pattern 1: top K with a heap of size K

To keep the **K largest**, use a **min-heap of size K**. When it grows bigger than K, pop the smallest. At the end `h[0]` is the K-th largest.

```python
def kth_largest(nums, k):
    h = []
    for x in nums:
        heapq.heappush(h, x)
        if len(h) > k:
            heapq.heappop(h)
    return h[0]

print(kth_largest([3, 2, 1, 5, 6, 4], 2))   # -> 5
```

Cost: O(n log k). It is the reverse of what you expect: keep the K largest with a **min**-heap.

## Pattern 2: count, then heap of tuples

Top K frequent: count with a dict, push `(-count, item)`, pop K times.

## Pattern 3: k-way merge

Push the first item of each source with its position `(value, source, index)`. Pop the smallest, then push the next item of the same source.

## Pattern 4: greedy with a heap

At every step take the best available item (largest profit, smallest rope, most frequent task), then update what is available. Examples: connect ropes, IPO, task scheduler.

## Pattern 5: two heaps (median)

A max-heap for the small half, a min-heap for the big half. Keep sizes equal (or small half one bigger). The median is at the top of one or between both tops.

## Common mistakes

- Using a max-heap pattern with plain `heapq` (it is a min-heap): forget the negatives.
- Forgetting to negate again after `heappop`.
- Pushing items that cannot be compared (use tuples that start with a number).
- Sorting everything when a size-K heap is enough.
- Treating `h` as sorted: only `h[0]` is the smallest.

## Interview corner

**Q: Why O(n log k) for the K-th largest?**
A: Each of the n pushes costs log k because the heap never grows beyond k + 1 items.

**Q: Heap vs sorting?**
A: Sorting is O(n log n) and gives everything. A heap is better when you need only the top few, or items arrive over time.

**Q: How do you get a max-heap in Python?**
A: Push negated values (or negated counts in a tuple).

**Q: How do two heaps give a median?**
A: One holds the smaller half (max-heap), the other the bigger half (min-heap). Their tops are the middle values.

## Summary

- `heapq` is a min-heap on a list: `heappush`, `heappop`, `h[0]`, `heapify`.
- Top K: heap of size K. Frequencies: tuples. Many sources: k-way merge. Medians: two heaps.
- References: `reference/heap-and-deque.md`, `reference/patterns.md`.

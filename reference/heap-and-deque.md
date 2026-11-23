# `heapq` and `deque`

Both come from the standard library. Import them first:

```python
import heapq
from collections import deque
```

## `heapq`: a min-heap on a plain list

A heap keeps the **smallest** item at index 0. Push and pop cost O(log n); reading the smallest costs O(1).

| Call | What it does |
| --- | --- |
| `heapq.heappush(h, x)` | add `x` |
| `heapq.heappop(h)` | remove and return the smallest |
| `h[0]` | peek at the smallest (does not remove) |
| `heapq.heapify(h)` | turn a list into a heap in O(n) |
| `heapq.heappushpop(h, x)` | push `x`, then pop and return the smallest (faster than two calls) |
| `heapq.nlargest(k, items)` / `nsmallest` | the k biggest / smallest, sorted |

```python
h = []
for x in [5, 1, 4]:
    heapq.heappush(h, x)
print(heapq.heappop(h))    # -> 1
print(h[0])                # -> 4
```

**Max-heap trick:** push the negative (`-x`) and negate again when you pop.

```python
h = []
for x in [5, 1, 4]:
    heapq.heappush(h, -x)
print(-heapq.heappop(h))   # -> 5
```

**Pairs:** push tuples. Python compares the first item, then the second:

```python
heapq.heappush(h, (count, word))     # smallest count first
```

**Gotcha:** the list `h` is only a heap if you change it with `heapq` functions. `h.sort()` or `h.append(x)` breaks it. Printing `h` does not show sorted order.

## `deque`: a fast queue

`list.pop(0)` is O(n). A `deque` removes from the left in O(1).

| Call | What it does |
| --- | --- |
| `q = deque([1, 2])` | create |
| `q.append(x)` / `q.appendleft(x)` | add right / left |
| `q.popleft()` / `q.pop()` | remove left / right |
| `q[0]`, `len(q)`, `while q:` | peek, size, loop |

```python
q = deque([1, 2, 3])
print(q.popleft())    # -> 1
q.append(4)
print(list(q))        # -> [2, 3, 4]
```

**Gotcha:** `popleft()` on an empty deque raises `IndexError`. Check `while q:` first.

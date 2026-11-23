# Sets

Unique, unordered items. Items must be hashable (numbers, strings, tuples).

| Tool | Does | Returns |
| --- | --- | --- |
| `set(items)` | unique items | set |
| `s.add(x)` | add | `None` |
| `s.discard(x)` | remove if present | `None` |
| `s.remove(x)` | remove, error if missing | `None` |
| `x in s` | membership, fast | bool |
| `a \| b` | union | set |
| `a & b` | intersection | set |
| `a - b` | only in a | set |
| `a ^ b` | in exactly one | set |

## Create
```python
print(set([1, 1, 2, 3, 3]))   # -> {1, 2, 3}
empty = set()                  # {} is a dict!
```

## Membership is fast
**Theory:** a set hashes the item and jumps to it, so `in` takes about the same time for 10 or 10 million items. A list scans.
```python
s = {1, 2, 3}
print(2 in s)   # -> True
```

## Set math
```python
a, b = {1, 2, 3}, {2, 3, 4}
print(a | b, a & b, a - b, a ^ b)   # -> {1, 2, 3, 4} {2, 3} {1} {1, 4}
```

## Seen-set pattern
```python
def first_repeat(items):
    seen = set()
    for x in items:
        if x in seen:
            return x
        seen.add(x)
    return None
print(first_repeat([3, 1, 4, 1]))   # -> 1
```

## Order
No order, no indexing. Use `sorted(s)` for a list in order.
**Gotcha:** `0`, `0.0` and `False` are equal to a set. Lesson: `dsa/09-sets`.

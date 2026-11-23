# Remove duplicates without mutating

Write `dedupe(items)` that returns a **new list** with duplicates removed, keeping the **first occurrence order**. The input list must not be changed.

```python
data = [3, 1, 3, 2, 1]
dedupe(data)   # -> [3, 1, 2]
data           # -> [3, 1, 3, 2, 1]
```

Items are hashable. Aim for O(n) — no `list.count` or `in` checks on a list inside a loop. (Hint: dicts keep insertion order, or use a seen-set.)

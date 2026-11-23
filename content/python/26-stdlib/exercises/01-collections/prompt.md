# Pick the right collection

Write:

1. `top_words(text, n)` → the `n` most common lowercase words as `[(word, count), ...]`. Words are split on whitespace; ignore case. Ties keep the order of first appearance (that's what `Counter.most_common` does).
2. `group_by_domain(emails)` → dict mapping domain → list of emails (in input order), using `defaultdict`. Return a plain `dict`.
3. `class RecentEvents(limit)` → `add(event)` stores events, keeping only the last `limit`; `items()` returns them as a list, oldest first. Use a `deque`.

```python
top_words("the cat and THE hat the end", 2)   # -> [("the", 3), ("cat", 1)]
group_by_domain(["a@x.io", "b@y.io", "c@x.io"])  # -> {"x.io": ["a@x.io", "c@x.io"], "y.io": ["b@y.io"]}
r = RecentEvents(2); r.add(1); r.add(2); r.add(3); r.items()   # -> [2, 3]
```

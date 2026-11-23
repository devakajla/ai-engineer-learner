# Post-filter the results

Write `post_filter(results, where, k)`. `results` is a list of search results, best first. Each result is a dictionary with an `"id"` and a `"metadata"` dictionary. `where` is a dictionary of required metadata values, for example `{"source": "auth.md"}`.

Keep the results whose metadata has **every** key of `where` with an equal value. Keep their order. Return at most `k`.

Rules:
- An empty `where` (`{}`) keeps everything.
- A result whose metadata lacks a key of `where` does not match.
- `k <= 0` gives `[]`.
- Do not change the input list.

```python
results = [
    {"id": "a", "metadata": {"source": "tasks.md", "lang": "en"}},
    {"id": "b", "metadata": {"source": "auth.md", "lang": "en"}},
    {"id": "c", "metadata": {"source": "auth.md", "lang": "hi"}},
]
[r["id"] for r in post_filter(results, {"source": "auth.md"}, 5)]               # -> ['b', 'c']
[r["id"] for r in post_filter(results, {"source": "auth.md", "lang": "hi"}, 5)] # -> ['c']
[r["id"] for r in post_filter(results, {}, 2)]                                  # -> ['a', 'b']
```

**Think first:** when the filter is strict, how many results can come back? What does that mean for the size of the candidate list you ask the index for?

# Filter the hits for a user

`allowed(chunk, user)` (exercise 1) is in the starter. Write `filter_hits(hits, user)`. It returns the hits the user may see, in the **same order**. A hit is a dictionary that has `"tenant"` and maybe `"groups"` like a chunk.

```python
hits = [{"id": "a", "tenant": "acme"}, {"id": "b", "tenant": "other"}, {"id": "c", "tenant": "acme", "groups": ["hr"]}]
filter_hits(hits, {"tenant": "acme", "groups": ["dev"]})
# -> [{'id': 'a', 'tenant': 'acme'}]
```

Do not change the list you were given.

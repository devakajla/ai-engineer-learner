# Plan an incremental update

Re-embedding every document on every run is slow and costs money. An **incremental update** only touches what changed.

`content_hash(text)` (exercise 2) is in the starter. Write `plan_sync(stored, docs)`.

- `stored` is a dictionary `{doc_id: hash}` of what the index already has.
- `docs` is a dictionary `{doc_id: text}` of the documents now.

Return a dictionary with four lists of doc ids. Each list is **sorted**:
- `"add"`: ids in `docs` but not in `stored`.
- `"update"`: ids in both, where `content_hash(docs[id])` differs from `stored[id]`.
- `"delete"`: ids in `stored` but not in `docs`.
- `"same"`: ids in both with the same hash.

```python
stored = {"a": content_hash("old"), "b": content_hash("same"), "gone": "x"}
docs = {"a": "new", "b": "same", "c": "fresh"}
plan_sync(stored, docs)
# -> {'add': ['c'], 'update': ['a'], 'delete': ['gone'], 'same': ['b']}
```

**Think first:** what happens in your index if you never handle `"delete"`?

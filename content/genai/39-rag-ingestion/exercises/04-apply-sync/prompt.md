# Apply the update

Now do the work. In the starter: `content_hash` and `plan_sync` (exercises 2 and 3).

Write `apply_sync(index, docs, embed)`.

- `index` is a dictionary `{doc_id: {"hash": ..., "vector": ...}}`. **Change it in place.**
- `docs` is `{doc_id: text}`.
- `embed(texts)` takes a list of texts and returns a list of vectors, one per text.

Rules:
1. Get `stored = {doc_id: entry["hash"]}` from the index, and the plan from `plan_sync(stored, docs)`.
2. Embed **only** the added and updated documents, in **one** call to `embed`, in sorted id order. If there is nothing to embed, do **not** call `embed`.
3. For each of them set `index[doc_id] = {"hash": content_hash(text), "vector": vector}`.
4. Remove the deleted ids from `index`.
5. Return `{"added": n, "updated": n, "deleted": n, "same": n}` (counts).

```python
index = {}
apply_sync(index, {"a": "x", "b": "y"}, embed)    # -> {'added': 2, 'updated': 0, 'deleted': 0, 'same': 0}
apply_sync(index, {"a": "x", "b": "y"}, embed)    # -> {'added': 0, 'updated': 0, 'deleted': 0, 'same': 2}   (no embed call)
```

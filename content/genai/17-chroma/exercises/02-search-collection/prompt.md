# Search a collection

Write `search(collection, embed, query, k=3)`. It returns the `k` chunks closest to the query.

The collection uses **cosine distance**. Each result is a dictionary:

```python
{"id": ..., "text": ..., "source": ..., "heading": ..., "score": ...}
```

`score` is `1 - distance`, so bigger is better.

Rules:
- Embed the query with `embed([query])[0]`.
- Use `collection.query(query_embeddings=[vector], n_results=...)`. Ask for no more than `collection.count()` results.
- Results come back as lists inside lists: take `[0]` of `ids`, `documents`, `metadatas` and `distances`.
- Best match first (Chroma already orders them).
- If `k <= 0` or the collection is empty, return `[]` and do not call `embed`.

```python
search(collection, embed, "delete a task", k=1)
# -> [{'id': 'a', 'text': 'delete a task', 'source': 'tasks.md', 'heading': '', 'score': 1.0}]
```

**Think first:** what happens when `k` is bigger than the number of chunks?

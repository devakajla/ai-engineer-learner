# Index a document and search it

The whole Level 3 chain in one function: cut a document into chunks (lesson 16), store them in Chroma (this lesson), and search.

Given in the starter: `chunk_document` (the last lesson's exercise), `add_chunks` (exercise 1) and `search` (exercise 2). Write `index_and_search(collection, embed, name, md, query, max_chars=300, k=3)`.

Rules:
1. Make the chunks with `chunk_document(name, md, max_chars)`.
2. Store them with `add_chunks(collection, embed, chunks)`.
3. Return `search(collection, embed, query, k)`.

```python
hits = index_and_search(collection, embed, "tasks.md", md, "how do I delete a task", k=1)
hits[0]["source"]    # -> 'tasks.md'
hits[0]["heading"]   # -> 'Delete'
```

Calling it twice with the same document must not create duplicates (the chunk ids are the same, and `add_chunks` upserts).

**Think first:** what would go wrong if two documents had chunks with the same ids?

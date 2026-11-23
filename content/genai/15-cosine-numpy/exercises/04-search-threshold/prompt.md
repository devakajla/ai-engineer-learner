# Search with a minimum score

A search always returns *something*, even when nothing is really close. In a RAG app this is dangerous: the model would answer from a bad page. The fix is a **minimum score**: results below it are thrown away. If nothing is left, the app can say "I don't know".

`search_texts(embed, query, texts, k)` is in the starter (your last exercise). Write `search_with_threshold(embed, query, texts, k=3, min_score=0.0)`.

Rules:
- Get the top `k` hits with `search_texts`.
- Keep only the hits whose score is `>= min_score`. Keep the order.
- Return `[]` when none are left.

```python
def embed(texts):
    return [[t.count("task"), t.count("login")] for t in texts]

docs = ["delete a task", "login with a token", "weather today"]
search_with_threshold(embed, "task", docs, k=3, min_score=0.5)
# -> [('delete a task', 1.0)]
search_with_threshold(embed, "pizza", docs, k=3, min_score=0.5)
# -> []        (nothing is close: time to say "I don't know")
```

**Think first:** what score would a good "min_score" be for real embeddings? How would you find out?

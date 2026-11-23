# Search texts

Write `search_texts(embed, query, texts, k=3)`. It finds the texts that are closest in meaning to the query.

`embed` is a function. It takes a **list of texts** and returns a **list of vectors** (one per text). The starter gives you `cosine_scores(query_vector, doc_vectors)`, which returns a list with one cosine score per document.

Rules:
- Call `embed` **once** with all the texts, and **once** with `[query]`. If `texts` is empty, return `[]` and do not call `embed` for the texts.
- Return the top `k` as a list of `(text, score)` pairs, best score first. Ties: the earlier text first.
- If `k <= 0`, return `[]`. If `k` is bigger than the number of texts, return all of them.

```python
def embed(texts):                       # a tiny fake: [count of "task", count of "login"]
    return [[t.count("task"), t.count("login")] for t in texts]

docs = ["delete a task", "login with a token", "list every task and task"]
search_texts(embed, "task", docs, k=2)
# -> [('delete a task', 1.0), ('list every task and task', 1.0)]
search_texts(embed, "login", docs, k=1)
# -> [('login with a token', 1.0)]
```

**Think first:** why is it better to embed all the texts in one call?

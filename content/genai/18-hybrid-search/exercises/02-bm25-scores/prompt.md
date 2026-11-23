# BM25 scores

Write `bm25_scores(query, docs, k1=1.5, b=0.75)`. `query` is a text and `docs` is a list of texts. Return one BM25 score per document, in the same order, as plain floats.

The starter gives you `tokenize`. Use it for the query and for every document.

For each **unique** query word `t` (keep it once even if the query repeats it), add this to a document's score:

```
idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_length / avg_doc_length))
```

- `tf`: how many times `t` appears in the document's tokens.
- `df`: how many documents contain `t` at least once.
- `N`: the number of documents.
- `idf = math.log(1 + (N - df + 0.5) / (df + 0.5))`
- `doc_length`: the number of tokens in the document. `avg_doc_length`: the average over all documents.

Rules:
- A word with `tf == 0` adds nothing to that document.
- No documents: return `[]`. If `avg_doc_length` is 0 (all documents are empty), return all `0.0`.

```python
bm25_scores("b", ["a b", "a c c"])        # -> [0.7617..., 0.0]
bm25_scores("zzz", ["a b", "a c c"])      # -> [0.0, 0.0]
bm25_scores("a", [])                      # -> []
```

**Think first:** which numbers are the same for all documents, and can be worked out once before the loop?

**Hint:** `import math`, `dict.fromkeys(words)` keeps unique words in order, `tokens.count(word)`.

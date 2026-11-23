# Hybrid search

Join keyword search and vector search. In the starter you have `bm25_scores(query, docs)` (exercise 2), `reciprocal_rank_fusion(rankings)` (exercise 3) and `rank_indexes(scores)`. `rank_indexes` gives the indexes of a score list, best score first (equal scores keep their order).

Write `hybrid_search(query, docs, vector_scores, k=3)`. `vector_scores[i]` is the vector similarity of `docs[i]` to the query (you get it from your embedder, as in lesson 15).

Rules:
- If `k <= 0` or `docs` is empty, return `[]`.
- The **vector ranking** is `rank_indexes(vector_scores)`.
- The **keyword ranking** is `rank_indexes(bm25_scores(query, docs))`, but **only** indexes whose BM25 score is above 0. A document with no keyword match must not get a keyword rank.
- Fuse both rankings with `reciprocal_rank_fusion([vector_ranking, keyword_ranking])`.
- Return the top `k` as `(doc text, fused score)` pairs, best first.

```python
docs = ["error E1042 means bad token", "how to log in", "delete a task"]
hybrid_search("E1042", docs, vector_scores=[0.1, 0.8, 0.2], k=2)
# the vector search prefers "how to log in", but only doc 0 contains E1042
# -> [('error E1042 means bad token', ...), ('how to log in', ...)]
```

**Think first:** why must a doc with zero keyword score be left out of the keyword ranking?

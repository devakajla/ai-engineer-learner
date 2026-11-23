# Step 11 — Hybrid search

Vector search is weak at exact words like `429` or `X-API-Key`. In this step Copilot gets a second searcher, **BM25**, and joins both rankings with **reciprocal rank fusion**. No new library is needed.

### 1. Keyword search: `copilot/bm25.py`

```python
"""Keyword search with BM25. Pure functions, no model calls."""

import math

PUNCTUATION = ".,;:!?()\"'`"


def tokenize(text):
    """Lowercase words. Punctuation is stripped from the ends of each word, the inside is kept."""
    words = []
    for word in text.lower().split():
        word = word.strip(PUNCTUATION)
        if word:
            words.append(word)
    return words


def bm25_scores(query, docs, k1=1.5, b=0.75):
    """One BM25 score per document text, in the same order."""
    if not docs:
        return []
    tokenized = [tokenize(doc) for doc in docs]
    n = len(docs)
    avg_length = sum(len(tokens) for tokens in tokenized) / n
    if avg_length == 0:
        return [0.0] * n
    scores = [0.0] * n
    for term in dict.fromkeys(tokenize(query)):
        df = 0
        for tokens in tokenized:
            if term in tokens:
                df += 1
        if df == 0:
            continue
        idf = math.log(1 + (n - df + 0.5) / (df + 0.5))
        for i, tokens in enumerate(tokenized):
            tf = tokens.count(term)
            if tf == 0:
                continue
            norm = tf + k1 * (1 - b + b * len(tokens) / avg_length)
            scores[i] += idf * tf * (k1 + 1) / norm
    return scores


def rank_by_score(scores):
    """Indexes of the scores, best first, skipping zeros. Ties: lower index first."""
    pairs = [(-scores[i], i) for i in range(len(scores)) if scores[i] > 0]
    pairs.sort()
    return [i for _, i in pairs]
```

`rank_by_score` skips chunks with a score of 0. A chunk that has none of the query words should not appear in the keyword ranking at all.

### 2. Hybrid search: `copilot/hybrid.py`

```python
"""Hybrid search: vector search plus BM25 keyword search, joined with reciprocal rank fusion."""

from copilot.bm25 import bm25_scores, rank_by_score
from copilot.embed import embed_texts
from copilot.store import build_where, search


def reciprocal_rank_fusion(rankings, k=60):
    """Join ranked lists of ids. Returns (id, score) pairs, best first. Ties: first seen wins."""
    scores = {}
    for ranking in rankings:
        for rank, item in enumerate(ranking, start=1):
            scores[item] = scores.get(item, 0.0) + 1 / (k + rank)
    pairs = list(scores.items())
    return sorted(pairs, key=pair_score, reverse=True)


def pair_score(pair):
    return pair[1]


def keyword_search(collection, query, k=20, source=None, heading=None):
    """The k best BM25 matches among the stored chunks, as dicts without a score."""
    where = build_where(source, heading)
    stored = collection.get() if where is None else collection.get(where=where)
    scores = bm25_scores(query, stored["documents"])
    hits = []
    for i in rank_by_score(scores)[:k]:
        hits.append({
            "id": stored["ids"][i],
            "text": stored["documents"][i],
            "source": stored["metadatas"][i]["source"],
            "heading": stored["metadatas"][i]["heading"],
        })
    return hits


def hybrid_search(collection, query, k=3, pool=20, source=None, heading=None, embed=embed_texts):
    """Vector and keyword search, fused. Each side gives `pool` candidates, the best k are returned.

    Each hit is {"id", "text", "source", "heading", "score"}. The score is the RRF score.
    """
    if k <= 0:
        return []
    vector_hits = search(collection, query, k=pool, source=source, heading=heading, embed=embed)
    keyword_hits = keyword_search(collection, query, k=pool, source=source, heading=heading)
    by_id = {}
    for hit in vector_hits + keyword_hits:
        by_id[hit["id"]] = hit
    fused = reciprocal_rank_fusion([[h["id"] for h in vector_hits], [h["id"] for h in keyword_hits]])
    results = []
    for chunk_id, score in fused[:k]:
        hit = by_id[chunk_id]
        results.append({
            "id": chunk_id,
            "text": hit["text"],
            "source": hit["source"],
            "heading": hit["heading"],
            "score": score,
        })
    return results
```

Read `hybrid_search` slowly:

1. Ask the vector store for `pool` candidates (20).
2. Ask BM25 for `pool` candidates (20).
3. Remember each chunk by id (`by_id`), because a chunk may come from either side.
4. Fuse the two **id lists** with RRF, and keep the best `k`.

Why does `keyword_search` read every chunk from Chroma with `collection.get()`? BM25 needs the texts of all chunks to count how rare a word is. This is fine for thousands of chunks. For millions you would use an inverted index (a search engine like Elasticsearch, or Postgres full-text search).

### 3. Compare the three searches: `copilot/docs_cli.py`

Replace the file with:

```python
"""Index and search your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.docs_cli search "how do I delete a task"
    python -m copilot.docs_cli vector "how do I delete a task"
    python -m copilot.docs_cli keyword "error 429"
"""

import sys

from copilot.hybrid import hybrid_search, keyword_search
from copilot.store import index_folder, open_collection, search

DB_PATH = ".chroma"


def show(hits):
    for hit in hits:
        score = f"{hit['score']:.3f}" if "score" in hit else "-----"
        print(f"{score}  {hit['source']} [{hit['heading']}]")
        print("       " + hit["text"][:100].replace("\n", " "))


def main():
    commands = ("index", "search", "vector", "keyword")
    if len(sys.argv) < 3 or sys.argv[1] not in commands:
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    command, rest = sys.argv[1], sys.argv[2:]
    if command == "index":
        print(f"Indexed {index_folder(collection, rest[0])} chunks.")
    elif command == "search":
        show(hybrid_search(collection, " ".join(rest)))
    elif command == "vector":
        show(search(collection, " ".join(rest)))
    else:
        show(keyword_search(collection, " ".join(rest), k=3))


if __name__ == "__main__":
    main()
```

```bash
uv run python -m copilot.docs_cli keyword "429"
uv run python -m copilot.docs_cli vector "429"
uv run python -m copilot.docs_cli search "429"
```

Try an exact term from your docs, then a question in different words ("get rid of a todo item"). See which side finds what, and how the hybrid result mixes them. That is the lesson, live.

### 4. Commit

```bash
git add -A && git commit -m "Add BM25 keyword search and hybrid search with RRF"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 10)
│   ├── bm25.py
│   └── hybrid.py
├── docs/
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests check `tokenize`, `bm25_scores` (rare words, length, empty input), `rank_by_score`, `reciprocal_rank_fusion` (ties, items in both lists win), `keyword_search` (filters) and `hybrid_search` with a fake `embed`: a chunk that only the keyword side can find must still appear. Steps 1 to 10 must keep working.

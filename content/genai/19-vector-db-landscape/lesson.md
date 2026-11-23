---
title: "Vector DB landscape: pgvector, Qdrant, Pinecone"
summary: Learn how fast vector search really works (exact vs approximate, HNSW), how filters and memory limits matter, and how to choose between Chroma, pgvector, Qdrant and Pinecone.
plan_ids: []
---

You have used numpy and Chroma. Real jobs use other tools too, and interviewers ask "which vector database would you pick, and why?" This lesson gives you the map. There is no new project step here. The Copilot project keeps all vector code in one file (`copilot/store.py`), so switching a database later means changing that one file.

You will not install the other databases in this lesson. The code shown for them is for reading. Always check the current docs, because these tools change fast.

## Exact search vs approximate search

**Exact search** (also called brute force or "flat"): compare the query with every vector, keep the best. This is what your numpy `top_k` did. It always finds the true nearest vectors. But the cost grows with the number of vectors:

- 10,000 vectors: instant.
- 1,000,000 vectors: slow for a web request (hundreds of milliseconds or more, depending on hardware).
- 100,000,000 vectors: not realistic.

**Approximate nearest neighbour (ANN)** search builds an **index** (a helper structure) so it can skip most vectors. It is much faster, but it may miss a true neighbour once in a while. It trades a little **accuracy** for a lot of **speed**.

How do you measure the accuracy? **Recall@k**: of the true top `k` neighbours, what fraction did the index return?

```python
truth = ["a", "b", "c", "d"]       # the real top 4 (from exact search)
found = ["a", "c", "x", "d"]       # what the ANN index returned

hits = [i for i in found if i in truth]
print(hits)                        # -> ['a', 'c', 'd']
print(len(hits) / len(truth))      # -> 0.75        recall@4 = 75%
```

A recall of 0.95 or more is usually good enough for RAG. You can raise recall by making the index search more carefully, at the cost of speed.

## Two index ideas

You do not need the maths. Just the pictures.

**HNSW** (Hierarchical Navigable Small World). Vectors are nodes in a graph, and each node is linked to its near neighbours. The graph has layers: a thin top layer with long jumps, and denser layers below. A search starts at the top, jumps toward the query, and goes down layer by layer, like zooming in on a map. It is fast and accurate, and it is the most common index today (Chroma, pgvector, Qdrant and others use it). Cost: it uses a lot of **memory**, and building it takes time.

**IVF** (inverted file). Split all vectors into groups (clusters). At search time, find the few closest cluster centres, and only scan the vectors in those clusters. Cost: a query near a cluster border can miss neighbours in the next cluster. You tune how many clusters to scan.

A third trick, **quantization**, stores each number in fewer bits (for example 8 bits, or even 1 bit, in place of 32). It saves memory and speeds up search, with a small loss of accuracy.

## Memory: do the maths

Each number in a vector is usually a 32-bit float: **4 bytes**. So:

```
memory = number of vectors * dimension * bytes per number
```

### Step by step: how much memory?

Same pattern as the first exercise. First a different job: the size of a photo library. Each photo is `width * height` pixels, 3 bytes per pixel, and you have `count` photos.

1. Multiply: `count * width * height * 3`. This gives bytes.
2. Divide by `1_000_000` to get megabytes (MB).
3. Round to 2 decimals.

```python
def library_mb(count, width, height):
    total_bytes = count * width * height * 3
    return round(total_bytes / 1_000_000, 2)

print(library_mb(100, 1000, 1000))   # -> 300.0
print(library_mb(0, 1000, 1000))     # -> 0.0
```

For vectors it is the same shape: `n_vectors * dim * bytes_per_number`, then divide by a million. Try it: 1,000,000 vectors of 384 numbers is `1,000,000 * 384 * 4 = 1,536,000,000` bytes, which is **1536 MB**, about 1.5 GB. And an HNSW index adds extra memory for its graph links on top. So "how many vectors do we have?" is the first question when you choose a database.

## Filters: a hard problem

You often search with a filter: "chunks from `tasks.md`", "documents of user 42". There are two simple strategies, and both have a catch:

- **Post-filter:** search first (get the top `n`), then throw away results that do not match the filter. Problem: if the filter is strict, nothing may be left. You asked for 5, but only 1 of the top 20 matched.
- **Pre-filter:** filter first, then search only the matching vectors. Problem: with an ANN index, a strict filter can break the graph walk, so quality or speed drops.

Good databases have **filtered search** built into the index so that you get `k` results that all match. When you compare databases, test it with your own filters. A common (rough) workaround for post-filtering: ask for many more candidates than you need (`k * 10`), then filter.

```python
results = [
    {"id": "a", "metadata": {"source": "tasks.md"}},
    {"id": "b", "metadata": {"source": "auth.md"}},
    {"id": "c", "metadata": {"source": "auth.md"}},
]
kept = [r for r in results if r["metadata"]["source"] == "auth.md"]
print([r["id"] for r in kept])   # -> ['b', 'c']
```

## The main options

**Chroma.** Embedded in your Python program, simple, free. Great for learning, prototypes and small apps. Less suited for a big shared production service.

**pgvector.** An extension for **PostgreSQL**. Your vectors live next to your normal tables. You get SQL, joins, transactions, backups and permissions that you already know. Supports HNSW and IVFFlat indexes. For many apps, "just use Postgres" is the best answer, because there is no new system to run.

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE chunks (
    id serial PRIMARY KEY,
    source text,
    content text,
    embedding vector(384)
);
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

SELECT id, content, 1 - (embedding <=> '[0.1, 0.2, ...]') AS score
FROM chunks
WHERE source = 'tasks.md'
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

`<=>` is the cosine **distance** (so the score is `1 - distance`). `<->` is Euclidean distance. `<#>` is the negative inner product.

**Qdrant.** A dedicated vector database, written in Rust, open source, with a hosted cloud option. Strong filtering (it calls metadata "payload"), and built-in support for hybrid search. You run it with Docker. A good choice when vector search is the core of your product.

```python
# for reading: check the qdrant-client docs for your version
from qdrant_client import QdrantClient, models

client = QdrantClient(":memory:")
client.create_collection("docs", vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE))
client.upsert("docs", points=[models.PointStruct(id=1, vector=[0.1] * 384, payload={"source": "tasks.md"})])
hits = client.query_points("docs", query=[0.1] * 384, limit=3).points
```

**Pinecone.** A fully **managed** (hosted) service. No servers to run, easy scaling, and you pay for it. Good when the team prefers to buy and not to operate. It is closed source. Check current pricing on their site.

**Others you may hear about:** FAISS (a library from Meta, not a database, very fast, the building block under many tools), Weaviate, Milvus, Elasticsearch/OpenSearch (search engines with vector support), and Redis.

## How to choose

| Situation | Reasonable choice |
| --- | --- |
| Learning, prototype, under 100k vectors | numpy or Chroma |
| You already run Postgres, up to a few million vectors | **pgvector** |
| Vector search is the product, heavy filters, a lot of data | **Qdrant** (or similar) |
| You want zero operations and can pay | **Pinecone** (managed) |

Questions to ask: How many vectors, now and in a year? What filters? How many writes and updates? Who runs it (your team or a vendor)? Do you need hybrid search? What does it cost? **Start simple.** Most apps never outgrow pgvector.

## Try it live

1. Make 2,000 random vectors of 384 numbers with numpy. Time an exact search (matrix times query, then sort) for one query.
2. Use Chroma (it uses HNSW) with the same vectors. Time the same query. Is it faster? How many results match the exact top 10? That fraction is **recall@10**.
3. Work out by hand how many MB 5 million vectors of 768 numbers need. Is it a job for your laptop?

## A little deeper

- **Tuning knobs.** HNSW has `M` (links per node), `ef_construction` (build effort) and `ef_search` (query effort). A bigger `ef_search` means higher recall and slower queries. IVF has the number of clusters and how many to probe (`nprobe`).
- **Cosine vs dot vs L2.** Pick the distance your embedding model was trained with. For normalized vectors, all three rank the same.
- **Updates and deletes.** Many ANN indexes are good at inserts but handle deletes and updates less well (they mark entries as deleted and rebuild later). Know how your database handles it.
- **Multi-tenancy.** If each customer must only see their own data, use a filter on a tenant id (at minimum), or a separate collection per tenant. A missing filter is a data leak.
- **Changing the embedding model** means re-embedding everything and rebuilding the index. Plan for it. Keep the source text so that you can.
- **Disk vs memory.** Some systems keep the index on disk with a small cache, to save RAM. Slower, but cheaper at a large scale.
- **Hybrid search support.** Qdrant, Elasticsearch, Weaviate and Postgres (full-text search plus pgvector) can do keyword and vector in one place. With Chroma, you built it yourself in step 11.
- **Benchmarks lie a little.** Public numbers use their data and their hardware. Measure with your own vectors and filters.

## Common mistakes

- Choosing a heavy, separate system for 20,000 vectors.
- Staying on brute force when you have millions of vectors.
- Never measuring recall of the ANN index.
- Forgetting the memory cost of the index, not just the vectors.
- Post-filtering with a strict filter and getting fewer than `k` results.
- Forgetting the tenant filter in a multi-user app.
- Mixing distance and similarity (`<=>` is a **distance**).
- Changing the embedding model without re-embedding.

## Interview corner

**When would you use pgvector and when a dedicated vector database?**
pgvector when you already use Postgres and have up to a few million vectors: one system, SQL, transactions, joins. A dedicated database (Qdrant and similar) when you have a lot of vectors, heavy filtering, high query volume, or need features Postgres lacks.

**What is HNSW?**
A graph-based approximate nearest-neighbour index. A layered graph lets the search jump quickly toward the query. It is fast and accurate, but it uses a lot of memory.

**What does recall@k mean for an ANN index?**
The fraction of the true top-k neighbours (from exact search) that the index returns. You tune the index to get a recall that is high enough, with acceptable speed.

**How much memory do 5 million vectors with 768 dimensions need?**
`5,000,000 * 768 * 4 bytes = 15.36 GB` for float32, before the index overhead. Quantization can cut it a lot.

**Why is filtering hard in vector search?**
Post-filtering can leave fewer than k results, and pre-filtering can hurt the index's graph walk. Good databases have filter-aware search. Always test with your real filters.

## Summary

- Exact search is simple and right, but slow at scale. ANN indexes (HNSW, IVF) are fast and slightly inexact. Measure with recall@k.
- Memory = vectors * dimension * bytes per number (4 for float32), plus index overhead.
- Filters: post-filter can return fewer than k, pre-filter can hurt the index. Test with real filters.
- Chroma: learning and prototypes. pgvector: Postgres you already have. Qdrant: dedicated, strong filtering. Pinecone: managed.
- Start simple, measure, then move. Keep all vector code behind one file so the move is easy.
- Reference: `reference/genai-retrieval.md`.

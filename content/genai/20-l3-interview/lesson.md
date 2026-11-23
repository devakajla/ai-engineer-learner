---
title: Level 3 interview questions
summary: Embeddings, similarity, chunking, vector databases and hybrid search as interviewers ask them, with follow-up questions, short model answers and three timed coding exercises.
plan_ids: []
---

Level 3 is the "retrieval" half of RAG. Interviewers love it, because small choices (chunk size, distance, filters) change the quality a lot, and because you can **measure** the result.

How to use this lesson: **answer each question out loud first**, then read the model answer. The follow-up questions are the ones interviewers usually ask next.

Some words you will see:

- **Recall**: of the things you should find, how many did you find.
- **Precision**: of the things you found, how many were right.
- **Latency**: how long one search takes.
- **Corpus**: the whole set of documents you search.

## 1. Embeddings

**Q: What is an embedding, and why does search with embeddings work?**

**A:** An embedding is a fixed-length vector from a model trained so that texts with similar meaning get close vectors. So "nearest vector" means "most similar meaning". Search turns into a nearest-neighbour problem.

- *Follow-up: Can I compare embeddings from two models?* → No. Each model has its own space. Same model for documents and queries. Changing the model means re-embedding everything.
- *Follow-up: What is the dimension, and does bigger mean better?* → The vector length (384, 768, 1536...). More dimensions can hold more detail but cost more memory and time. Measure on your own data.
- *Follow-up: Local model or API model?* → Local: free, private, offline, you run the compute. API: no setup, scales, but costs per token and sends your text out. Pick by privacy, cost and quality needs.
- *Follow-up: Does the model need a prefix?* → Some do (a query prefix for retrieval). Read the model card. A missing prefix lowers quality.

## 2. Similarity

**Q: Cosine, dot product or Euclidean distance?**

**A:** Cosine compares direction and ignores length, which is what you want for text. For normalized (length 1) vectors, cosine and dot product are the same, and all three give the same ranking. Many models output normalized vectors, so the dot product is common and fast.

- *Follow-up: Range of cosine?* → -1 to 1. For text embeddings, mostly 0 to 1.
- *Follow-up: Similarity vs distance?* → Similarity: bigger is closer. Distance: smaller is closer. Cosine distance = 1 - cosine similarity. Check which one your library returns.
- *Follow-up: A zero vector?* → The cosine is undefined (divide by zero). Return 0 and never let `nan` into your ranking.
- *Follow-up: Top-k with numpy?* → One matrix-vector product, then `argsort` (or `argpartition`) on the scores.

## 3. Chunking

**Q: How do you chunk documents, and how do you pick the size?**

**A:** Use the structure of the document first (headings, then paragraphs), and fall back to a fixed size with a small overlap. Start with about 200 to 500 words, then measure retrieval on real questions and adjust. Keep metadata (source, heading, id) with each chunk.

- *Follow-up: Why overlap?* → So text near a border sits fully in at least one chunk. About 10 to 20%.
- *Follow-up: Chunks too big or too small?* → Too big: blurry vectors, wasted prompt tokens. Too small: lost context, answers split over chunks.
- *Follow-up: Parent-child retrieval?* → Search small chunks (sharp), then give the model the larger parent section (more context).
- *Follow-up: Code or tables?* → Never cut in the middle of a code block or a table. Treat them as units.
- *Follow-up: Chunk by characters or by tokens?* → Tokens match the model's limits better. Characters are a fine start.

## 4. Vector databases

**Q: Why do we need a vector database, and not just numpy?**

**A:** For persistence, metadata filters, updates and deletes, and fast approximate search at scale. For a few thousand vectors, numpy brute force is fine.

- *Follow-up: What is ANN, and what is recall@k?* → Approximate nearest neighbours skip most vectors using an index (HNSW, IVF). Recall@k is the share of the true top-k that the index returns. You trade a little recall for a lot of speed.
- *Follow-up: HNSW in one sentence?* → A layered graph of neighbours; search jumps from coarse to fine layers. Fast and accurate, memory hungry.
- *Follow-up: pgvector vs a dedicated database?* → pgvector if you already use Postgres and have up to a few million vectors. Dedicated (Qdrant and similar) for large scale, heavy filtering or special features.
- *Follow-up: How do you keep the index fresh?* → Stable chunk ids, upsert, delete the chunks of a changed source first, re-embed only changed files.
- *Follow-up: Memory for 1M vectors of 384 dims?* → `1,000,000 * 384 * 4` bytes, about 1.5 GB, plus index overhead.
- *Follow-up: Multi-tenant data?* → Always filter on a tenant id (or use separate collections). A missing filter is a data leak.

## 5. Hybrid search

**Q: What is hybrid search and why use it?**

**A:** Run vector search and keyword search (BM25) and join the results. Vectors catch meaning and synonyms. Keywords catch exact terms like error codes and names. Together they find more.

- *Follow-up: How does BM25 work?* → For each query word: rarity (idf) times how often it appears (flattened) with a length adjustment.
- *Follow-up: How do you combine the rankings?* → Reciprocal rank fusion: sum of `1 / (k + rank)`, with `k` about 60. It ignores score scales.
- *Follow-up: Why not add the scores?* → Different scales. One side would dominate.
- *Follow-up: How many candidates per side?* → More than you need (about 20 for a final 5), so fusion has overlap and choice.
- *Follow-up: What comes next to improve quality?* → A reranker over the fused top results, and query rewriting (Level 4).

## 6. Measuring retrieval

**Q: How do you know your retrieval is good?**

**A:** Build a small set of real questions, each with the chunk (or document) that should answer it. Run the search and compute **hit rate@k** (did the right chunk appear in the top k?) and **MRR** (mean reciprocal rank: the average of `1 / rank` of the right chunk). Change one thing at a time (chunk size, model, hybrid on or off) and compare.

- *Follow-up: Why not eyeball a few queries?* → Small changes help some questions and hurt others. Only a fixed set shows the net effect.
- *Follow-up: Hit rate vs MRR?* → Hit rate only says if it was in the top k. MRR also rewards a higher position.

## 7. Rapid-fire (one-liners)

- Is an embedding reversible to the text? → No (but it can leak information).
- Why batch the embedding calls? → Models are far faster per text in a batch.
- `1 - cosine_distance` gives? → The cosine similarity.
- Do vectors from model A and model B mix? → Never.
- Default distance in Chroma? → Squared Euclidean (l2). Set cosine yourself.
- Can `upsert` remove old chunks? → No. Delete them yourself.
- BM25 `b` controls? → Document length normalization.
- RRF rank starts at? → 1.
- When is brute force fine? → Up to about 100k vectors, often more.
- Why keep the heading in metadata? → For citations and filters.

## Tools for the coding exercises

Interview coding tasks here are small, careful functions with maths. These tools cover the three exercises.

- **`zip(a, b)`** walks two lists together.
- **`sum(x * y for x, y in zip(a, b))`** is the dot product. `sum(x * x for x in a) ** 0.5` is the length.
- **`sorted(items, reverse=True)`** and **tuples**: sort `(-score, index)` pairs to get "best score first, ties by the lower index".
- **`max(...)`** with `default=0` for an empty sequence: `max([], default=0)` gives `0`.
- **A "chosen" list and a "remaining" list**: pick the best remaining item, move it to chosen, repeat `k` times.
- **`enumerate(items, start=1)`** gives 1-based ranks.
- **Dividing by the count** of runs; guard the empty case first.

## How to practise

1. Set a timer: 20 minutes per exercise.
2. Write the plan in plain words first, then the code.
3. Test the edge cases: empty input, zero vectors, `k` bigger than the list, ties.
4. Say your reasoning out loud, as if an interviewer were listening.
5. When you finish, ask Claude to review your code in the side panel.

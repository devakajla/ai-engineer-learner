# GenAI retrieval: embeddings, numpy, chunking, Chroma, BM25

Used in `genai/14-20`. Each entry: the call, what it means, an example, a gotcha.

## Embeddings (fastembed, local)
```python
from fastembed import TextEmbedding
model = TextEmbedding("BAAI/bge-small-en-v1.5")         # downloads about 130 MB once
vectors = [v.tolist() for v in model.embed(["a", "b"])]  # one 384-number list per text
```
An embedding is a fixed-length list of numbers. Similar meaning, close vectors.
**Gotcha:** use the same model for documents and queries. Changing the model means re-embedding everything. Embed in batches (one call for many texts).

## Dot product and distance (pure Python)
```python
sum(x * y for x, y in zip(a, b))             # dot product
sum((x - y) ** 2 for x, y in zip(a, b)) ** 0.5   # Euclidean distance
```
**Gotcha:** `zip` stops at the shorter list without any warning. Check `len(a) == len(b)` yourself.

## numpy
```python
import numpy as np
a = np.array([3.0, 4.0])
np.dot(a, b)                  # dot product
np.linalg.norm(a)             # length -> 5.0
matrix @ query                # dot product of every row with query
np.linalg.norm(matrix, axis=1)    # one length per row
np.argsort(-scores, kind="stable")[:k]   # indexes of the top k, best first, ties by lower index
```
**Gotcha:** `argsort` goes small to big, so negate the scores. numpy numbers are `np.float64`/`np.int64`: wrap with `float()`/`int()` when returning plain values. Printing a list of numpy ints in numpy 2 shows `np.int64(1)`.

## Cosine similarity
```python
cosine = dot(a, b) / (norm(a) * norm(b))     # 1 same direction, 0 unrelated, -1 opposite
```
**Gotcha:** a zero vector has length 0. Return `0.0`, never `nan`. Cosine distance = `1 - cosine`. For length-1 vectors, cosine equals the dot product.

## Chunking
```python
text[start:start + size]                  # slice, safe past the end
start += size - overlap                   # sliding window step
text.split("\n\n")                        # paragraphs
line.lstrip("#")                          # heading level = len(line) - len(stripped)
```
Fixed size with overlap, paragraph packing, markdown headings. Keep metadata: `id`, `source`, `heading`, `text`.
**Gotchas:** `overlap >= size` never ends. Add the last chunk after a packing loop. Lines inside code fences (```) are not headings.

## Chroma
```python
import chromadb
client = chromadb.EphemeralClient()          # memory. PersistentClient(path=".chroma") for disk
col = client.get_or_create_collection("docs", embedding_function=None, metadata={"hnsw:space": "cosine"})
col.upsert(ids=[...], documents=[...], embeddings=[...], metadatas=[{"source": "a.md"}])
r = col.query(query_embeddings=[vec], n_results=3, where={"source": "a.md"})
r["ids"][0], r["documents"][0], r["metadatas"][0], r["distances"][0]   # lists inside lists
score = 1 - distance                          # cosine space
col.get(where={...}); col.delete(where={...}); col.count()
```
**Gotchas:** the default distance is not cosine. `where={}` and two keys in one `where` are errors (use `{"$and": [...]}`). Empty lists in `upsert` are errors. Metadata values: str, int, float, bool only. `upsert` does not remove old chunks.

## BM25 (keyword search)
```python
idf = math.log(1 + (N - df + 0.5) / (df + 0.5))
score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * doc_len / avg_len))     # k1 about 1.5, b 0.75
```
`df`: documents that contain the word. `tf`: count in this document.
**Gotcha:** count `df` per document, not per occurrence. Guard `avg_len == 0`. Tokens: lowercase, strip punctuation from the ends only.

## Reciprocal rank fusion
```python
score[id] += 1 / (k + rank)      # rank starts at 1, k about 60, summed over every list
```
**Gotcha:** use ranks, not raw scores, because cosine and BM25 are on different scales. Take more candidates per side (20) than you return (5).

## Retrieval metrics
```python
recall_at_k = len(set(truth[:k]) & set(found[:k])) / len(truth[:k])
hit_rate = share of questions whose right chunk is in the top k
mrr = mean of 1 / rank of the right chunk (0 if not in the top k)
```
**Gotcha:** a result at rank 4 does not count for `k = 3`.

## RAG: context, citations, rerank (Level 4)
```python
context = "\n\n".join(f"[{n}] {hit['text']}" for n, hit in enumerate(hits, start=1))   # numbered chunks
```
Rules of the pipeline: no good hits means "I don't know" without a model call. Check every `[n]` in the answer against the number of chunks. Retrieve wide (20+), rerank, send the top 3 to 5.
**Gotcha:** `enumerate(items, start=1)` gives 1-based numbers. The model cites what you printed, so keep the same list.

## Hash a document (ingestion)
```python
import hashlib
hashlib.sha256(" ".join(text.split()).encode("utf-8")).hexdigest()[:16]    # -> 16-character fingerprint
```
Same text gives the same hash. Normalize spaces first, so a layout-only change is not an update. Compare hashes to get add / update / delete / same.
**Gotcha:** `.encode("utf-8")` is needed, the hash works on bytes. Deleted or shrunk documents leave stale chunks unless you delete them.

## Dates and age (freshness)
```python
from datetime import date
(date.fromisoformat("2026-11-23") - date.fromisoformat("2026-11-13")).days     # -> 10
```
**Gotcha:** an ISO text like `"2026-11-23"` must be turned into a date first. Subtracting two dates gives a `timedelta`, and `.days` is the number.

## More metrics: precision, nDCG
```python
precision_at_k = hits_in_top_k / k                       # divide by k even if fewer results came back
dcg = sum(rel / math.log2(pos + 1) for pos, rel in enumerate(grades[:k], start=1))
ndcg = dcg / ideal_dcg                                   # ideal = same grades sorted best first
```
**Gotcha:** guard `ideal_dcg == 0`. Raising k raises recall and lowers precision.

## LLM judge
Ask for JSON like `{"score": 1-5, "reason": "..."}`, temperature 0, tags around the answer. Parse safely: find `{` and `}`, `json.loads`, check `isinstance(score, bool)` first (in Python `True` is an `int`), and treat a bad reply as unscored.
**Gotcha:** judges prefer long answers and the first answer. Check the judge against human grades.

# 12. Vector databases

You have embeddings for thousands of chunks. Given a question, how do you find the closest few **fast**? With 1,000 chunks, the numpy loop of chapter 10 is fine. With 10 million, it is far too slow. A **vector database** is built for exactly this.

## What a vector database does

It stores vectors **with** their text and metadata, and answers: "give me the K vectors nearest to this query vector", optionally **filtered** by metadata. That query is called **nearest-neighbour search**.

@@ flow | Figure 12.1: what you ask and what you get.
Query vector|from the user's question|blue -> Vector DB|nearest-neighbour search;plus metadata filter|yellow -> Top K chunks|text, metadata, distance|green
@@ end

## Why not compare with everything?

**Exact search** compares the query with every vector: perfect results, but the time grows with the data. 10 million vectors of 384 numbers means billions of operations per query.

**Approximate nearest neighbour (ANN)** search builds a clever **index** in advance, so a query only looks at a small part of the data. It might miss the true best match now and then, in return for being 100 or 1000 times faster. That trade-off is **recall versus latency**.

Two index families you should know:

- **HNSW** (Hierarchical Navigable Small World): a layered graph. A search starts at the top, which has few well-connected points, jumps toward the query, and goes down layer by layer to zoom in, like finding a street by moving from country to city to street. Fast and accurate, uses a lot of memory. This is the most common choice.
- **IVF** (inverted file): first group the vectors into clusters. At query time, find the few closest cluster centres and search only inside them. Uses less memory, but you must tune how many clusters to visit.

Settings you will meet: how many neighbours each node keeps and how widely a search explores (higher means better recall and slower queries). **Recall** is the share of the true top-K that the index actually returned. Aim for something like 95 percent or more, and measure it.

## Chroma: the easy start

**Chroma** runs inside your Python program, with no server, and can save to disk. It is perfect for learning and small projects. Install: `uv add chromadb`.

```python
import chromadb

client = chromadb.EphemeralClient()      # in memory; use PersistentClient(path="./chroma") to save
collection = client.create_collection(
    "support_docs",
    embedding_function=None,                 # we supply our own vectors
    metadata={"hnsw:space": "cosine"},       # compare with cosine distance
)

collection.add(
    ids=["1", "2", "3"],
    embeddings=[embed(d).tolist() for d in docs],
    documents=docs,
    metadatas=[{"src": "a"}, {"src": "b"}, {"src": "a"}],
)
```

What each part is:

- A **collection** is like a table: one set of vectors for one purpose.
- `ids` must be unique strings. `embeddings` are the vectors. `documents` is the text. `metadatas` is a dict per chunk.
- `embedding_function=None` says "I will pass vectors myself". If you leave Chroma's default, it quietly downloads its own model the first time. Being explicit avoids surprises, and guarantees the **same** embedder for documents and queries.
- `hnsw:space: cosine` chooses the distance. Without it, Chroma uses L2.

Querying, using the toy embedder from chapter 10:

```python
query_vector = embed("how do I reset my password to login")

result = collection.query(query_embeddings=[query_vector.tolist()], n_results=2)
print(result["ids"])
# -> [['2', '3']]
print([round(d, 2) for d in result["distances"][0]])
# -> [-0.0, 1.0]
```

The result holds lists inside lists, one inner list per query. Chroma returns **distance**, not similarity. For cosine, `distance = 1 - similarity`, so **smaller is better**: document 2 has distance 0 (a perfect match, the `-0.0` is rounding noise), and document 3 has 1.0 (unrelated).

### Filtering by metadata

```python
result = collection.query(
    query_embeddings=[query_vector.tolist()],
    n_results=2,
    where={"src": "b"},
)
print(result["ids"])
# -> [['2']]
```

Only chunks whose `src` is `"b"` were considered. This is how you restrict a search to one customer's documents, one product, or one language. **Filters are how you do multi-tenant safety** (chapter 20), so never skip them.

Other everyday calls: `collection.upsert(...)` (add or replace by id), `collection.delete(ids=[...])`, `collection.get(ids=[...])`, `collection.count()`.

> In tests, give each collection a **unique name**. The in-process Chroma client shares state inside one program, so a repeated name returns the old data.

## The landscape

| Option | What it is | Good for |
| --- | --- | --- |
| **Chroma** | embedded, simple Python library | learning, prototypes, small apps |
| **pgvector** | a Postgres extension | when your data is already in Postgres; one system for rows and vectors |
| **Qdrant** | dedicated vector DB (open source), strong filtering | production search at scale |
| **Pinecone** | fully managed service | when you do not want to run anything |
| **Weaviate, Milvus** | other dedicated systems | large deployments, extra features |
| **FAISS** | a library of index algorithms, not a database | custom or research setups |

**pgvector in a few lines** (SQL; not run here), to show how little changes if you already use Postgres:

```sql
CREATE EXTENSION vector;
CREATE TABLE chunks (id serial PRIMARY KEY, body text, embedding vector(384), tenant_id int);
CREATE INDEX ON chunks USING hnsw (embedding vector_cosine_ops);

SELECT id, body FROM chunks
WHERE tenant_id = 7
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

`<=>` is the cosine distance operator. The query is plain SQL, so you get joins, transactions and backups for free. For most projects up to a few million vectors, pgvector is a very reasonable choice.

## Operating a vector store

- **Updates and deletes.** When a source document changes, delete its old chunks (use a `doc_id` in metadata) and insert the new ones. Stale chunks give stale answers.
- **Re-embedding.** A new embedding model means re-embedding **everything** into a **new** collection, then switching over. Store the model name in metadata so you can tell.
- **Memory.** 100,000 vectors of 384 float32 numbers is about 150 MB, before the index. HNSW adds overhead.
- **Backups and persistence.** An in-memory store loses data at exit. Use a persistent path or server.
- **Filters and index.** Heavy filtering can hurt recall in some systems. Test with your real filters.

::: {.box .checkpoint}
**Checkpoint:** you can explain exact versus approximate search, what recall means, and why Chroma returns smaller-is-better distances.
:::

## Common mistakes

::: {.box .mistake}
**Common mistakes**

- Letting Chroma use a default embedder different from the one you use for queries.
- Reading `distance` as similarity (higher is **worse**).
- No metadata filter in a multi-user system.
- Never deleting old chunks when documents change.
- Switching embedding models without re-indexing.
- Keeping an in-memory store and expecting it to survive a restart.
:::

## Interview corner

::: {.box .interview}
**Interview corner**

**Q: Why use a vector database?** It stores vectors with metadata and finds nearest neighbours fast with an index, which a brute-force scan cannot do at scale.

**Q: What is HNSW?** A multi-layer graph index for approximate nearest-neighbour search. It navigates from coarse to fine layers toward the query, giving high recall at low latency, at a memory cost.

**Q: Recall vs latency?** ANN indexes trade accuracy for speed. Tuning search breadth raises recall but slows queries.

**Q: pgvector or a dedicated vector DB?** pgvector keeps everything in Postgres and is simple for moderate scale. A dedicated system (Qdrant, Pinecone) gives more scale and filtering features.

**Q: How do you update a vector index when documents change?** Delete the document's old chunks by id or `doc_id`, add the new chunks, and re-embed everything when the model changes.
:::

## Exercises

::: {.box .exercise}
**Exercises**

1. Create a Chroma collection with your toy embedder, add six documents, and query it.
2. Add metadata `{"lang": "en"}` or `{"lang": "hi"}` and query with a `where` filter.
3. Write `reindex_document(collection, doc_id, chunks)` that deletes old chunks of the document and adds new ones.
4. Add the same ids twice with `add` and then with `upsert`. What is the difference?
5. Estimate the memory for 2 million vectors of 768 numbers (float32).
6. **Think:** your index returns the true best match 90 percent of the time. What happens in a RAG answer when it misses?
:::

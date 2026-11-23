---
title: A vector database with Chroma
summary: Store chunks and their vectors in Chroma once, search them by meaning, and filter the search with metadata.
plan_ids: []
---

In lesson 15 your search embedded **every** document **on every question**. That is slow, and it throws work away. A **vector database** fixes this: it stores the vectors, so you embed each chunk once, and it searches them fast.

In this lesson you use **Chroma**: free, open source, runs inside your Python program, no server to install. It is a good first vector database.

## What a vector database does

Four jobs:

1. **Store** vectors together with their text and metadata.
2. **Search** the nearest vectors to a query vector.
3. **Filter** by metadata (only chunks from `tasks.md`).
4. **Persist**: keep the data on disk, so you do not rebuild it on every start.

It is a normal database where the key search is "nearest vectors" and not "equal value".

Install it in your own project with `uv add chromadb`.

## Collections

A **collection** is like a table. It holds chunks that belong together. You make a client, then ask for a collection:

```python
import chromadb

client = chromadb.EphemeralClient()     # lives in memory, gone when the program ends
collection = client.get_or_create_collection(
    "docs",
    embedding_function=None,
    metadata={"hnsw:space": "cosine"},
)
```

Two settings matter:

- `embedding_function=None`: Chroma can embed text by itself with a default model, but you want **control**. You make the vectors (with `embed_texts` from lesson 15's project), and you give them to Chroma. Same model for documents and questions, as always.
- `"hnsw:space": "cosine"`: how to measure closeness. The **default is not cosine** (it is squared Euclidean distance). Say `cosine` on purpose. (Newer Chroma versions may also offer a `configuration=` argument for the same thing. Check the docs for your version.)

Collection names need 3 to 512 characters, from letters, digits, `.`, `_` and `-`.

For data that must survive a restart, use a client with a folder:

```python
client = chromadb.PersistentClient(path=".chroma")
```

Add `.chroma/` to `.gitignore`. It is generated data.

## Adding chunks

Use `upsert`. It means "insert, or update if the id exists". Running your ingest twice then does not create duplicates.

```python
collection.upsert(
    ids=["a", "b", "c"],
    documents=["delete a task", "login with a token", "list tasks"],
    embeddings=[[1.0, 0.0, 0.1], [0.0, 1.0, 0.1], [0.9, 0.0, 0.1]],
    metadatas=[{"source": "tasks.md"}, {"source": "auth.md"}, {"source": "tasks.md"}],
)
print(collection.count())    # -> 3
```

Four lists, **all the same length**, in the same order:

- `ids`: unique strings. Your stable chunk ids (`tasks.md:0`) fit perfectly.
- `documents`: the chunk texts.
- `embeddings`: one vector per document.
- `metadatas`: one dictionary per chunk.

Rules for metadata: values must be a string, int, float or bool. No `None`, no lists, no nested dictionaries. An empty string `""` for "no heading" is fine.

> `upsert` with empty lists raises an error. Check `if not chunks: return` before calling it.

### Step by step: from chunks to the four lists

Your chunks are dictionaries like `{"id": ..., "source": ..., "heading": ..., "text": ...}`. Chroma wants parallel lists. Same pattern as the first exercise, shown with a different shape of data: names and ages.

Goal: from `people = [{"name": "Asha", "age": 30}, ...]` build `names`, `ages` and a `labels` list.

1. If the list is empty, return early.
2. Build each list with a comprehension. Keep the same order every time.
3. Check that all lists have the same length (they will, because they come from the same source).

```python
people = [{"name": "Asha", "age": 30}, {"name": "Ravi", "age": 25}]

names = [p["name"] for p in people]
ages = [p["age"] for p in people]
labels = [{"age": p["age"]} for p in people]

print(names)    # -> ['Asha', 'Ravi']
print(ages)     # -> [30, 25]
print(labels)   # -> [{'age': 30}, {'age': 25}]
```

For chunks: `ids = [c["id"] for c in chunks]`, and so on. Embed the texts in **one batch call**: `embed(texts)`.

## Searching

```python
result = collection.query(
    query_embeddings=[[1.0, 0.0, 0.1]],
    n_results=2,
)
print(result["ids"])         # -> [['a', 'c']]
print(result["documents"])   # -> [['delete a task', 'list tasks']]
print(result["distances"])   # -> [[1.2e-07, 6.0e-05]]   (tiny, because both are close to the query)
```

Notice the **double lists**. You can send many queries at once, so every field is a list with one inner list per query. With one query, take `[0]`:

```python
ids = result["ids"][0]
texts = result["documents"][0]
distances = result["distances"][0]
metadatas = result["metadatas"][0]
```

The result has **distances**, and smaller means closer. (The first one is not exactly 0 because Chroma stores 32-bit floats. Tiny noise like `1.2e-07` is normal.) With cosine, `distance = 1 - similarity`. So convert back if you want a score where bigger is better:

```python
score = 1 - distance
```

If you ask for more results than the collection holds, you get what is there. If the collection is empty, guard first with `collection.count()`.

## Filtering with metadata

Often you want to search only a part of the data: one file, one version, one language. Pass a `where` dictionary:

```python
collection.query(query_embeddings=[[1.0, 0.0, 0.1]], n_results=2, where={"source": "tasks.md"})
```

Filter operators start with `$`:

```python
{"source": "tasks.md"}                       # equal (short form)
{"source": {"$in": ["tasks.md", "auth.md"]}} # one of
{"version": {"$gt": 1}}                      # greater than
{"$and": [{"source": "tasks.md"}, {"heading": "Delete"}]}   # both
{"$or": [{"source": "a.md"}, {"source": "b.md"}]}           # either
```

Two traps:

- `where={}` (empty) is an **error**. Pass `None`, or leave it out.
- `{"source": "a.md", "heading": "x"}` with two keys is also an error. Use `$and`.

So building a `where` takes care: none given gives `None`, one given gives a single condition, two given gives `$and`.

## Other things you will use

```python
collection.get(ids=["a"])                # fetch by id
collection.get(where={"source": "auth.md"})
collection.delete(ids=["a"])
collection.count()
client.delete_collection("docs")
```

To re-index a changed file, delete the chunks of that source (`collection.delete(where={"source": "tasks.md"})`) and upsert the new ones. Otherwise chunks that no longer exist stay in the index. Stale data gives wrong answers.

## The whole chain in one function

Level 3 so far: cut a document (lesson 16), embed and store the chunks (this lesson), search. Joining them gives you a mini search engine over any markdown file.

Let's practise the shape with a different example: three small steps joined by one function that only calls them.

```python
def clean(text):
    return text.strip()

def shout(text):
    return text.upper()

def make_title(text):
    return shout(clean(text))

make_title("  hello ")   # -> 'HELLO'
```

`make_title` has almost no logic. It joins tested pieces, in order. The fourth exercise is the same: chunk, store, search.

## Try it live

1. Build a collection with a real `fastembed` embedder. Index `reference/genai-groq.md` and `reference/genai-retrieval.md` with your chain.
2. Ask 5 real questions and print the top 2 hits for each (source, heading and score).
3. Run the index step twice. Check that `collection.count()` does not change. Why not?

## A little deeper

- **How the search is fast: HNSW.** Chroma does not compare the query with every vector. It builds a graph (HNSW: Hierarchical Navigable Small World) where neighbours are linked, and walks it. This gives **approximate** nearest neighbours: very fast, and almost always right. Lesson 19 explains the trade-off.
- **Why a distance?** Databases index by distance (smaller is nearer). Libraries differ, so always read the docs: some give similarity, some give distance, some give a negative dot product.
- **Do not mix embedding models in one collection.** Different models, different spaces. Use one collection per model, or store the model name in the collection metadata.
- **Dimension is fixed by the first insert.** Adding a vector with a different length later fails.
- **Chroma's own embedding function.** If you do not pass `embedding_function=None` and you send `documents` without embeddings, Chroma downloads a default model and embeds for you. Convenient, but hidden. In this track we embed ourselves, so we know what happens.
- **Client modes.** `EphemeralClient` (memory), `PersistentClient` (disk), and `HttpClient` (talk to a Chroma server). The collection code is the same.
- **Concurrency.** A `PersistentClient` is fine for one program. For many web workers writing at once, use a server (Chroma server, Qdrant, pgvector).
- **Telemetry.** Chroma may send anonymous usage data by default. Turn it off with `chromadb.config.Settings(anonymized_telemetry=False)`, passed as `settings=` to the client. The Copilot project does this.
- **Version changes.** Chroma changes fast. If an example fails, check the docs of the version you installed.

## Common mistakes

- Forgetting `"hnsw:space": "cosine"` and reading the default distance as a cosine distance.
- Treating distance like a score, so "bigger is better" is wrong.
- Forgetting the extra list: `result["documents"][0]`.
- `where={}` or two keys in one `where`.
- Calling `upsert` with an empty list.
- Metadata with `None` or a list value.
- Not deleting old chunks when a file changes.
- Mixing documents embedded by one model with queries by another.
- Using a random id each time, so every ingest adds duplicates. Use a stable id.

## Interview corner

**What does a vector database give you that a numpy array does not?**
Persistence, metadata filtering, updates and deletes, and fast approximate search that scales past what a brute-force scan can handle. For a few thousand vectors, numpy is enough.

**What is a `where` filter used for?**
Restricting the search to a part of the data (by source, version, tenant, language) so you never return chunks the user should not see or that are the wrong kind.

**Chroma returns distance. How do you turn it into a score?**
With a cosine space, `score = 1 - distance`. Always check the space the collection uses.

**How do you keep the index in sync when a document changes?**
Use stable ids and `upsert`, and delete the chunks of that source first, so removed text disappears. Re-embed only changed files.

## Summary

- A vector database stores vectors with text and metadata, searches nearest neighbours, filters, and persists.
- Chroma: `get_or_create_collection(name, embedding_function=None, metadata={"hnsw:space": "cosine"})`.
- `upsert(ids, documents, embeddings, metadatas)`: four lists of the same length. Stable ids avoid duplicates.
- `query(query_embeddings=[v], n_results=k, where=...)` returns lists inside lists. Take `[0]`. Score = `1 - distance` for cosine.
- `where` needs `$and` for two conditions and must not be empty.
- Project: step 10 adds `copilot/store.py` and `copilot/docs_cli.py`.
- Reference: `reference/genai-retrieval.md`.

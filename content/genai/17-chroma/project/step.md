# Step 10 — A vector store

Step 8 embedded every text on every question. Now you embed each chunk **once** and keep it in **Chroma**, so a question only costs one embedding and a fast search.

In your project folder:

```bash
uv add chromadb
echo ".chroma/" >> .gitignore
```

### 1. The store: `copilot/store.py`

```python
"""The vector store: Chroma holds the chunks, their vectors and their metadata."""

import chromadb
from chromadb.config import Settings

from copilot.embed import embed_texts
from copilot.ingest import ingest_folder

COLLECTION = "docs"
SETTINGS = Settings(anonymized_telemetry=False)   # do not send usage data


def open_collection(path=None, name=COLLECTION):
    """A cosine collection. With a path the data is saved on disk, without one it lives in memory."""
    if path:
        client = chromadb.PersistentClient(path=path, settings=SETTINGS)
    else:
        client = chromadb.EphemeralClient(settings=SETTINGS)
    return client.get_or_create_collection(
        name,
        embedding_function=None,   # we make the vectors ourselves
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(collection, chunks, embed=embed_texts):
    """Embed the chunks in one batch and upsert them. Returns how many were added."""
    if not chunks:
        return 0
    texts = [c["text"] for c in chunks]
    collection.upsert(
        ids=[c["id"] for c in chunks],
        documents=texts,
        embeddings=embed(texts),
        metadatas=[{"source": c["source"], "heading": c["heading"]} for c in chunks],
    )
    return len(chunks)


def build_where(source=None, heading=None):
    """The Chroma filter for the given source and/or heading, or None for no filter."""
    conditions = []
    if source is not None:
        conditions.append({"source": source})
    if heading is not None:
        conditions.append({"heading": heading})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


def search(collection, query, k=3, source=None, heading=None, embed=embed_texts):
    """The k chunks closest to the query. Each is {"id", "text", "source", "heading", "score"}."""
    where = build_where(source, heading)
    if where is None:
        matching = collection.count()
    else:
        matching = len(collection.get(where=where)["ids"])
    if k <= 0 or matching == 0:
        return []
    vector = embed([query])[0]
    result = collection.query(query_embeddings=[vector], n_results=min(k, matching), where=where)
    hits = []
    for i, chunk_id in enumerate(result["ids"][0]):
        metadata = result["metadatas"][0][i]
        hits.append({
            "id": chunk_id,
            "text": result["documents"][0][i],
            "source": metadata["source"],
            "heading": metadata["heading"],
            "score": 1 - result["distances"][0][i],
        })
    return hits


def index_folder(collection, folder, max_chars=800, embed=embed_texts):
    """(Re)index a docs folder. Chunks of removed sections are deleted first. Returns the chunk count."""
    chunks = ingest_folder(folder, max_chars)
    for source in sorted({c["source"] for c in chunks}):
        collection.delete(where={"source": source})
    return add_chunks(collection, chunks, embed=embed)
```

Points to notice:

- **One place talks to Chroma.** No other file imports `chromadb`. If you switch to Qdrant or pgvector later (lesson 19), only this file changes.
- `Settings(anonymized_telemetry=False)` stops Chroma from sending usage data. Your choice, but good to know it exists.
- `open_collection(path)`: with a path the index is saved on disk (`.chroma/`), so you do not re-embed on every start. Without a path it lives in memory, which is what tests use.
- `embed=embed_texts` is again a default argument that tests replace with a fake.
- `index_folder` first **deletes** the old chunks of each file it re-reads, then upserts the new ones. Without that, a section you removed from a doc would stay in the index and could still be returned.
- `search` builds the filter in `build_where`. It never passes an empty `{}`, and uses `$and` for two conditions.

### 2. Try it: `copilot/docs_cli.py`

```python
"""Index and search your docs. Usage:

    python -m copilot.docs_cli index docs
    python -m copilot.docs_cli search "how do I delete a task"
"""

import sys

from copilot.store import index_folder, open_collection, search

DB_PATH = ".chroma"


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ("index", "search"):
        print(__doc__)
        return
    collection = open_collection(DB_PATH)
    if sys.argv[1] == "index":
        count = index_folder(collection, sys.argv[2])
        print(f"Indexed {count} chunks.")
        return
    for hit in search(collection, " ".join(sys.argv[2:])):
        print(f"{hit['score']:.3f}  {hit['source']} [{hit['heading']}]")
        print("       " + hit["text"][:100].replace("\n", " "))


if __name__ == "__main__":
    main()
```

```bash
uv run python -m copilot.docs_cli index docs
uv run python -m copilot.docs_cli search "how do I delete a task"
```

The first `index` downloads the embedding model (once) and embeds your chunks. After that, `search` is quick. Run `index` twice: the count stays the same, because the ids are stable.

Look at the scores. Ask something that is **not** in your docs ("what is the capital of France?"). The best score is lower, but there is still a "best" result. A search always returns something. Keep this in mind. Level 4 adds a minimum score so Copilot can say "I don't know".

### 3. Commit

```bash
git add -A && git commit -m "Add Chroma vector store and docs CLI"
```

### Expected structure

```
devdocs-copilot/
├── copilot/
│   ├── (files from step 9)
│   ├── docs_cli.py
│   └── store.py
├── docs/
├── .chroma/          (generated, ignored by git)
├── .env.example
├── .gitignore
├── pyproject.toml
└── uv.lock
```

### Checkpoint

The hidden tests use an in-memory collection and a fake `embed`. They check `add_chunks` (metadata, no duplicates, empty list), `build_where`, `search` (best first, filters, `k` too big, empty collection), `index_folder` (removed chunks disappear on re-index), and a disk collection that keeps its data after reopening. Steps 1 to 9 must keep working.

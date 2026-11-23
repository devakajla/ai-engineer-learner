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

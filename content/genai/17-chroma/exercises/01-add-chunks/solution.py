def add_chunks(collection, embed, chunks):
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

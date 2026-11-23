def search(collection, embed, query, k=3):
    count = collection.count()
    if k <= 0 or count == 0:
        return []
    vector = embed([query])[0]
    result = collection.query(query_embeddings=[vector], n_results=min(k, count))
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

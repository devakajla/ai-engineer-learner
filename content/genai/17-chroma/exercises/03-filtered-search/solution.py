def build_where(source=None, heading=None):
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


def search_filtered(collection, embed, query, k=3, source=None, heading=None):
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

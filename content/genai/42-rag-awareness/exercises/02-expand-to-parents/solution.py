def expand_to_parents(hits, parent_of, parents):
    order = []
    best = {}
    texts = {}
    for hit in hits:
        parent_id = parent_of.get(hit["id"])
        if parent_id is None:
            key = hit["id"]
            text = hit["text"]
        else:
            key = parent_id
            text = parents[parent_id]
        if key not in best:
            order.append(key)
            best[key] = hit["score"]
            texts[key] = text
        elif hit["score"] > best[key]:
            best[key] = hit["score"]
    return [{"id": key, "text": texts[key], "score": best[key]} for key in order]

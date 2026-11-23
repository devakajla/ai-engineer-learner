def dedupe_hits(hits, max_per_source=None):
    seen = []
    per_source = {}
    kept = []
    for hit in hits:
        normal = " ".join(hit["text"].lower().split())
        if normal in seen:
            continue
        source = hit.get("source", "")
        if max_per_source is not None and per_source.get(source, 0) >= max_per_source:
            continue
        seen.append(normal)
        per_source[source] = per_source.get(source, 0) + 1
        kept.append(hit)
    return kept

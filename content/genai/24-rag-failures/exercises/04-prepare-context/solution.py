# Given from earlier exercises. Do not change these.
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


def prepare_context(hits, max_hits, max_per_source=2):
    if max_hits <= 0:
        return []
    hits = dedupe_hits(hits, max_per_source)[:max_hits]
    front = hits[0::2]
    back = hits[1::2]
    back.reverse()
    return front + back

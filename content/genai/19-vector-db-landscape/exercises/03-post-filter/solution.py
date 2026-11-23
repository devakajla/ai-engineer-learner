def matches(metadata, where):
    for key, value in where.items():
        if key not in metadata or metadata[key] != value:
            return False
    return True


def post_filter(results, where, k):
    if k <= 0:
        return []
    kept = []
    for result in results:
        if matches(result["metadata"], where):
            kept.append(result)
            if len(kept) == k:
                break
    return kept

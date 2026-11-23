def recall_at_k(found, truth, k):
    if k <= 0:
        raise ValueError("k must be positive")
    wanted = truth[:k]
    if not wanted:
        return 1.0
    returned = found[:k]
    hits = [item for item in wanted if item in returned]
    return len(hits) / len(wanted)

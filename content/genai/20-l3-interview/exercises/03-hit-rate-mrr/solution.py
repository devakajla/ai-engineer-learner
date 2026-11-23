def retrieval_metrics(runs, k):
    if k <= 0:
        raise ValueError("k must be positive")
    if not runs:
        return {"hit_rate": 0.0, "mrr": 0.0}
    hits = 0
    reciprocal_sum = 0.0
    for retrieved, relevant in runs:
        top = retrieved[:k]
        if relevant in top:
            hits += 1
            reciprocal_sum += 1 / (top.index(relevant) + 1)
    return {"hit_rate": hits / len(runs), "mrr": reciprocal_sum / len(runs)}

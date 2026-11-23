# Given from earlier exercises. Do not change these.
def recall_at_k(expected_ids, retrieved_ids, k):
    if not expected_ids:
        return 1.0
    top = retrieved_ids[:k] if k > 0 else []
    found = sum(1 for item in expected_ids if item in top)
    return found / len(expected_ids)


def reciprocal_rank(expected_ids, retrieved_ids):
    for position, item in enumerate(retrieved_ids, start=1):
        if item in expected_ids:
            return 1 / position
    return 0.0


def precision_at_k(expected_ids, retrieved_ids, k):
    if k <= 0:
        return 0.0
    top = retrieved_ids[:k]
    good = sum(1 for item in top if item in expected_ids)
    return good / k


def evaluate_retrieval(retrieve, cases, k=5):
    if not cases:
        return {"n": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "misses": []}
    recall_total = 0.0
    precision_total = 0.0
    rr_total = 0.0
    misses = []
    for case in cases:
        hits = retrieve(case["question"], k)
        retrieved = [hit["id"] for hit in hits]
        recall = recall_at_k(case["expected"], retrieved, k)
        recall_total += recall
        precision_total += precision_at_k(case["expected"], retrieved, k)
        rr_total += reciprocal_rank(case["expected"], retrieved)
        if case["expected"] and recall == 0.0:
            misses.append(case["question"])
    n = len(cases)
    return {
        "n": n,
        "recall": round(recall_total / n, 4),
        "precision": round(precision_total / n, 4),
        "mrr": round(rr_total / n, 4),
        "misses": misses,
    }

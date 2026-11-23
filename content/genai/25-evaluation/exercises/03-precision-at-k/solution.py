def precision_at_k(expected_ids, retrieved_ids, k):
    if k <= 0:
        return 0.0
    top = retrieved_ids[:k]
    good = sum(1 for item in top if item in expected_ids)
    return good / k

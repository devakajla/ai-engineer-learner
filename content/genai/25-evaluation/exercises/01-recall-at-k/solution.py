def recall_at_k(expected_ids, retrieved_ids, k):
    if not expected_ids:
        return 1.0
    top = retrieved_ids[:k] if k > 0 else []
    found = sum(1 for item in expected_ids if item in top)
    return found / len(expected_ids)

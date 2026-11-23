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


# Your task:
def evaluate_retrieval(retrieve, cases, k=5):
    ...

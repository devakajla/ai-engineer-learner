def reciprocal_rank(expected_ids, retrieved_ids):
    for position, item in enumerate(retrieved_ids, start=1):
        if item in expected_ids:
            return 1 / position
    return 0.0

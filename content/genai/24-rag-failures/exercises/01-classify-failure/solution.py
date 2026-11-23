def classify_failure(expected_ids, retrieved_ids, answer_ok):
    if not expected_ids:
        return "ok" if answer_ok else "hallucination"
    found = any(item in retrieved_ids for item in expected_ids)
    if not found:
        return "retrieval_miss"
    if not answer_ok:
        return "generation_miss"
    return "ok"

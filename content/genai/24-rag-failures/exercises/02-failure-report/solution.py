# Given from earlier exercises. Do not change these.
CATEGORIES = ["ok", "retrieval_miss", "generation_miss", "hallucination"]


def classify_failure(expected_ids, retrieved_ids, answer_ok):
    if not expected_ids:
        return "ok" if answer_ok else "hallucination"
    found = any(item in retrieved_ids for item in expected_ids)
    if not found:
        return "retrieval_miss"
    if not answer_ok:
        return "generation_miss"
    return "ok"


def failure_report(results):
    counts = {name: 0 for name in CATEGORIES}
    by_category = {name: [] for name in CATEGORIES}
    for result in results:
        name = classify_failure(result["expected"], result["retrieved"], result["answer_ok"])
        counts[name] += 1
        by_category[name].append(result["question"])
    return {"counts": counts, "by_category": by_category}

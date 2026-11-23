"""Measure retrieval with numbers. A change you cannot measure is only a feeling."""

import json
from pathlib import Path

from copilot.embed import embed_texts
from copilot.hybrid import keyword_search
from copilot.rag import retrieve
from copilot.store import search


def recall_at_k(expected_ids, retrieved_ids, k):
    """The share of expected chunks found in the first k results. No expected chunks gives 1.0."""
    if not expected_ids:
        return 1.0
    top = retrieved_ids[:k] if k > 0 else []
    found = sum(1 for item in expected_ids if item in top)
    return found / len(expected_ids)


def reciprocal_rank(expected_ids, retrieved_ids):
    """1 divided by the position of the first expected chunk. 0.0 if none was found."""
    for position, item in enumerate(retrieved_ids, start=1):
        if item in expected_ids:
            return 1 / position
    return 0.0


def precision_at_k(expected_ids, retrieved_ids, k):
    """The share of the first k results that are expected. Always divides by k."""
    if k <= 0:
        return 0.0
    top = retrieved_ids[:k]
    good = sum(1 for item in top if item in expected_ids)
    return good / k


# Three retrievers with the SAME signature, so they can be compared on the same cases.
def vector_retriever(collection, question, k, embed):
    return search(collection, question, k=k, embed=embed)


def keyword_retriever(collection, question, k, embed):
    return keyword_search(collection, question, k=k)


def hybrid_retriever(collection, question, k, embed):
    return retrieve(collection, question, k=k, embed=embed)


RETRIEVERS = {"vector": vector_retriever, "keyword": keyword_retriever, "hybrid": hybrid_retriever}


def evaluate_retrieval(retriever, collection, cases, k=5, embed=embed_texts):
    """Run every case and average the scores.

    cases: [{"question": str, "expected": [chunk ids]}]. Returns n, recall, precision, mrr and
    "misses": the questions that had expected chunks but found none of them.
    """
    if not cases:
        return {"n": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "misses": []}
    recall_total = 0.0
    precision_total = 0.0
    rr_total = 0.0
    misses = []
    for case in cases:
        hits = retriever(collection, case["question"], k, embed)
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


def load_cases(path):
    """The golden set: a JSON list of {"question", "expected"}. A bad file gives a clear error."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("the golden file must hold a JSON list")
    for i, case in enumerate(data):
        if not isinstance(case, dict) or "question" not in case or not isinstance(case.get("expected"), list):
            raise ValueError(f"case {i} needs a question and an expected list")
    return data


def compare_retrievers(collection, cases, k=5, embed=embed_texts):
    """Evaluate vector, keyword and hybrid on the same cases. Returns {name: result}."""
    return {name: evaluate_retrieval(fn, collection, cases, k, embed) for name, fn in RETRIEVERS.items()}

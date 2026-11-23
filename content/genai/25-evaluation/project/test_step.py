"""Step 18 checks. Runs with the current directory = the learner's project folder."""

import json
import uuid

import pytest

from copilot.context import dedupe_hits
from copilot.evals import (
    RETRIEVERS,
    compare_retrievers,
    evaluate_retrieval,
    hybrid_retriever,
    keyword_retriever,
    load_cases,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    vector_retriever,
)
from copilot.store import add_chunks, open_collection


def embed(texts):
    """Fake embedder. It knows 'task', and that 'sign in' means 'login'. It knows nothing about numbers."""
    return [[t.lower().count("task"), t.lower().count("login") + t.lower().count("sign in"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [
    chunk(0, "tasks.md", "Create", "create a task with post"),
    chunk(1, "tasks.md", "Delete", "delete a task task task by id"),
    chunk(2, "errors.md", "Limits", "error 429 means too many requests"),
    chunk(3, "auth.md", "Login", "login with a token"),
]

CASES = [
    {"question": "login", "expected": ["auth.md:3"]},
    {"question": "429", "expected": ["errors.md:2"]},
    {"question": "the price of the moon", "expected": []},
]


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    assert len(dedupe_hits([{"text": "a"}, {"text": "A"}])) == 1


def test_recall_at_k():
    assert recall_at_k(["a", "b"], ["a", "x", "b"], 2) == 0.5
    assert recall_at_k(["a", "b"], ["a", "x", "b"], 3) == 1.0
    assert recall_at_k([], ["x"], 3) == 1.0, "nothing to find means nothing missed"
    assert recall_at_k(["a"], ["a"], 0) == 0.0


def test_reciprocal_rank():
    assert reciprocal_rank(["a"], ["x", "y", "a"]) == pytest.approx(1 / 3)
    assert reciprocal_rank(["a", "b"], ["b", "a"]) == 1.0
    assert reciprocal_rank(["a"], ["x"]) == 0.0 and reciprocal_rank(["a"], []) == 0.0


def test_precision_at_k():
    assert precision_at_k(["a", "b"], ["a", "x", "b", "y"], 4) == 0.5
    assert precision_at_k(["a"], ["a"], 3) == pytest.approx(1 / 3), "divide by k, not by the result count"
    assert precision_at_k(["a"], ["a"], 0) == 0.0


def test_evaluate_retrieval_empty():
    assert evaluate_retrieval(hybrid_retriever, filled(), [], k=3, embed=embed) == {
        "n": 0, "recall": 0.0, "precision": 0.0, "mrr": 0.0, "misses": [],
    }


def test_evaluate_retrieval_hybrid():
    result = evaluate_retrieval(hybrid_retriever, filled(), CASES, k=3, embed=embed)
    assert result["n"] == 3
    assert result["recall"] == 1.0, "hybrid must find both chunks, the 429 one through the keyword side"
    assert 0 < result["mrr"] <= 1
    assert result["misses"] == []


def test_keyword_search_is_blind_to_synonyms_and_finds_exact_terms():
    collection = filled()
    numbers = [{"question": "429", "expected": ["errors.md:2"]}]
    assert evaluate_retrieval(keyword_retriever, collection, numbers, k=1, embed=embed)["recall"] == 1.0
    synonym = [{"question": "sign in", "expected": ["auth.md:3"]}]
    assert evaluate_retrieval(keyword_retriever, collection, synonym, k=1, embed=embed)["recall"] == 0.0
    assert evaluate_retrieval(vector_retriever, collection, synonym, k=1, embed=embed)["recall"] == 1.0


def test_misses_list_the_questions():
    collection = filled()
    cases = [{"question": "429", "expected": ["errors.md:2"]}, {"question": "sign in", "expected": ["auth.md:3"]}]
    result = evaluate_retrieval(keyword_retriever, collection, cases, k=1, embed=embed)
    assert result["misses"] == ["sign in"]
    assert result["recall"] == 0.5


def test_compare_retrievers():
    results = compare_retrievers(filled(), CASES, k=3, embed=embed)
    assert list(results) == list(RETRIEVERS) == ["vector", "keyword", "hybrid"]
    assert results["hybrid"]["recall"] >= max(results["vector"]["recall"], results["keyword"]["recall"])


def test_load_cases(tmp_path):
    path = tmp_path / "golden.json"
    path.write_text(json.dumps(CASES))
    assert load_cases(path) == CASES
    path.write_text(json.dumps({"question": "x"}))
    with pytest.raises(ValueError):
        load_cases(path)
    path.write_text(json.dumps([{"question": "x"}]))
    with pytest.raises(ValueError):
        load_cases(path)
    path.write_text(json.dumps([{"question": "x", "expected": "a.md:1"}]))
    with pytest.raises(ValueError):
        load_cases(path)

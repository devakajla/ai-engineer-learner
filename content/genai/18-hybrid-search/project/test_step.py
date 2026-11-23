"""Step 11 checks. Runs with the current directory = the learner's project folder."""

import uuid

import pytest

from copilot.bm25 import bm25_scores, rank_by_score, tokenize
from copilot.hybrid import hybrid_search, keyword_search, reciprocal_rank_fusion
from copilot.store import add_chunks, open_collection, search


def embed(texts):
    """Fake embedder: [count of 'task', count of 'login', 0.1]. It knows nothing about numbers like 429."""
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [
    chunk(0, "tasks.md", "Create", "create a task with post, a task needs a title"),
    chunk(1, "tasks.md", "Delete", "delete a task task task by id"),
    chunk(2, "errors.md", "Limits", "error 429 means too many requests, slow down"),
    chunk(3, "auth.md", "Login", "login with a token"),
]


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    hits = search(filled(), "login", k=1, embed=embed)
    assert hits[0]["source"] == "auth.md"


def test_tokenize():
    assert tokenize("Use `DELETE /tasks/{id}`.") == ["use", "delete", "/tasks/{id}"]
    assert tokenize("... ?!") == [] and tokenize("") == []
    assert tokenize("Send the X-API-Key header.") == ["send", "the", "x-api-key", "header"]


def test_bm25_scores():
    scores = bm25_scores("b", ["a b", "a c c"])
    assert scores[0] == pytest.approx(0.7617, abs=1e-3) and scores[1] == 0.0
    assert bm25_scores("a", []) == [] and bm25_scores("a", ["", ""]) == [0.0, 0.0]
    docs = ["error code 429", "error in the app", "error while saving", "an error"]
    rare = bm25_scores("error 429", docs)
    assert rare.index(max(rare)) == 0


def test_rank_by_score():
    assert rank_by_score([0.0, 2.0, 0.5, 2.0, 0.0]) == [1, 3, 2], "best first, zeros skipped, ties: lower index first"
    assert rank_by_score([]) == []


def test_reciprocal_rank_fusion():
    result = reciprocal_rank_fusion([["a", "b", "c"], ["c", "a", "d"]])
    assert [i for i, _ in result] == ["a", "c", "b", "d"]
    assert dict(result)["a"] == pytest.approx(1 / 61 + 1 / 62)
    assert reciprocal_rank_fusion([["x"], ["y"]], k=1) == [("x", 0.5), ("y", 0.5)]
    assert reciprocal_rank_fusion([]) == []


def test_keyword_search_finds_exact_terms_and_respects_filters():
    collection = filled()
    hits = keyword_search(collection, "429")
    assert [h["id"] for h in hits] == ["errors.md:2"]
    assert set(hits[0]) == {"id", "text", "source", "heading"}
    assert keyword_search(collection, "task", source="tasks.md")[0]["id"] == "tasks.md:1"
    assert keyword_search(collection, "429", source="auth.md") == []
    assert keyword_search(collection, "nothing matches this") == []


def test_hybrid_finds_what_only_keywords_can_find():
    collection = filled()
    only_vector = search(collection, "task 429", k=1, embed=embed)
    assert only_vector[0]["source"] == "tasks.md", "the fake embedder cannot see 429"
    hybrid = hybrid_search(collection, "task 429", k=3, embed=embed)
    assert "errors.md:2" in [h["id"] for h in hybrid], "keyword search must bring the 429 chunk in"
    assert all(set(h) == {"id", "text", "source", "heading", "score"} for h in hybrid)
    scores = [h["score"] for h in hybrid]
    assert scores == sorted(scores, reverse=True)


def test_hybrid_both_sides_agree_wins_and_edges():
    collection = filled()
    top = hybrid_search(collection, "delete task task task", k=1, embed=embed)
    assert top[0]["id"] == "tasks.md:1"
    assert hybrid_search(collection, "task", k=0, embed=embed) == []
    assert len(hybrid_search(collection, "task", k=50, embed=embed)) <= 4
    filtered = hybrid_search(collection, "task 429", k=5, source="errors.md", embed=embed)
    assert {h["source"] for h in filtered} == {"errors.md"}

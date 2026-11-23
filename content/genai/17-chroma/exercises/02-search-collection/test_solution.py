import uuid

import chromadb
from chromadb.config import Settings
import pytest

from solution import search


def embed(texts):
    return [[t.count("task"), t.count("login"), 0.1] for t in texts]


def filled_collection():
    client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(
        f"t{uuid.uuid4().hex}", embedding_function=None, metadata={"hnsw:space": "cosine"}
    )
    texts = ["delete a task", "login with a token", "list every task"]
    collection.upsert(
        ids=["a", "b", "c"],
        documents=texts,
        embeddings=embed(texts),
        metadatas=[
            {"source": "tasks.md", "heading": "Delete"},
            {"source": "auth.md", "heading": ""},
            {"source": "tasks.md", "heading": "List"},
        ],
    )
    return collection


def test_best_match_first_with_fields():
    hits = search(filled_collection(), embed, "login", k=1)
    assert len(hits) == 1
    hit = hits[0]
    assert hit["id"] == "b" and hit["text"] == "login with a token"
    assert hit["source"] == "auth.md" and hit["heading"] == ""
    assert hit["score"] == pytest.approx(1.0, abs=0.05)


def test_order_and_scores_go_down():
    hits = search(filled_collection(), embed, "task", k=3)
    assert {h["id"] for h in hits[:2]} == {"a", "c"}
    assert hits[2]["id"] == "b"
    scores = [h["score"] for h in hits]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] > scores[2]


def test_k_bigger_than_count_and_edges():
    collection = filled_collection()
    assert len(search(collection, embed, "task", k=50)) == 3
    assert search(collection, embed, "task", k=0) == []
    client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    empty = client.get_or_create_collection(f"t{uuid.uuid4().hex}", embedding_function=None)
    called = []
    assert search(empty, lambda texts: called.append(texts) or [[0, 0, 0]], "x") == []
    assert called == [], "an empty collection: do not embed"

import uuid

import chromadb
from chromadb.config import Settings

from solution import build_where, search_filtered


def embed(texts):
    return [[t.count("task"), t.count("login"), 0.1] for t in texts]


def filled_collection():
    client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(
        f"t{uuid.uuid4().hex}", embedding_function=None, metadata={"hnsw:space": "cosine"}
    )
    texts = ["delete a task", "login with a token", "list every task", "logout of a task app"]
    collection.upsert(
        ids=["a", "b", "c", "d"],
        documents=texts,
        embeddings=embed(texts),
        metadatas=[
            {"source": "tasks.md", "heading": "Delete"},
            {"source": "auth.md", "heading": ""},
            {"source": "tasks.md", "heading": "List"},
            {"source": "auth.md", "heading": "Logout"},
        ],
    )
    return collection


def test_build_where():
    assert build_where() is None
    assert build_where(source="a.md") == {"source": "a.md"}
    assert build_where(heading="H") == {"heading": "H"}
    assert build_where("a.md", "H") == {"$and": [{"source": "a.md"}, {"heading": "H"}]}


def test_no_filter_searches_everything():
    hits = search_filtered(filled_collection(), embed, "task", k=10)
    assert {h["id"] for h in hits} == {"a", "b", "c", "d"}


def test_source_filter():
    hits = search_filtered(filled_collection(), embed, "task", k=10, source="auth.md")
    assert {h["id"] for h in hits} == {"b", "d"}
    assert all(h["source"] == "auth.md" for h in hits)


def test_both_filters():
    hits = search_filtered(filled_collection(), embed, "task", source="tasks.md", heading="List")
    assert [h["id"] for h in hits] == ["c"]


def test_empty_heading_can_be_filtered():
    hits = search_filtered(filled_collection(), embed, "login", heading="")
    assert [h["id"] for h in hits] == ["b"], "an empty string is a real value, not 'no filter'"


def test_nothing_matches_and_k_zero():
    collection = filled_collection()
    assert search_filtered(collection, embed, "task", source="missing.md") == []
    assert search_filtered(collection, embed, "task", k=0) == []

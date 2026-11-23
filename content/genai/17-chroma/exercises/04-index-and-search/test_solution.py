import uuid

import chromadb
from chromadb.config import Settings

from solution import index_and_search


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def new_collection():
    client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    return client.get_or_create_collection(
        f"t{uuid.uuid4().hex}", embedding_function=None, metadata={"hnsw:space": "cosine"}
    )


MD = "# Tasks\n\nCreate a task.\n\n## Delete\n\nDelete a task with DELETE.\n\n# Auth\n\nLogin with a token."


def test_finds_the_right_chunk():
    hits = index_and_search(new_collection(), embed, "api.md", MD, "login", k=1)
    assert len(hits) == 1
    assert hits[0]["source"] == "api.md"
    assert hits[0]["heading"] == "Auth"
    assert "token" in hits[0]["text"]


def test_no_duplicates_when_run_twice():
    collection = new_collection()
    index_and_search(collection, embed, "api.md", MD, "task")
    first_count = collection.count()
    index_and_search(collection, embed, "api.md", MD, "task")
    assert collection.count() == first_count == 3


def test_empty_document():
    assert index_and_search(new_collection(), embed, "e.md", "", "task") == []


def test_k_limits():
    hits = index_and_search(new_collection(), embed, "api.md", MD, "task", k=2)
    assert len(hits) == 2

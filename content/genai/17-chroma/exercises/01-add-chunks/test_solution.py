import uuid

import chromadb
from chromadb.config import Settings

from solution import add_chunks


def new_collection():
    client = chromadb.EphemeralClient(settings=Settings(anonymized_telemetry=False))
    return client.get_or_create_collection(
        f"t{uuid.uuid4().hex}", embedding_function=None, metadata={"hnsw:space": "cosine"}
    )


class Embed:
    """Fake embedder: [count of 'delete', count of 'get', 0.1]. Records calls."""

    def __init__(self):
        self.calls = []

    def __call__(self, texts):
        self.calls.append(list(texts))
        return [[t.lower().count("delete"), t.lower().count("get"), 0.1] for t in texts]


CHUNKS = [
    {"id": "t.md:0", "source": "t.md", "heading": "Delete", "text": "Use DELETE."},
    {"id": "t.md:1", "source": "t.md", "heading": "", "text": "Use GET."},
]


def test_adds_and_counts():
    collection = new_collection()
    embed = Embed()
    assert add_chunks(collection, embed, CHUNKS) == 2
    assert collection.count() == 2
    assert embed.calls == [["Use DELETE.", "Use GET."]], "embed all texts in ONE call, in order"


def test_data_is_stored_in_order():
    collection = new_collection()
    add_chunks(collection, Embed(), CHUNKS)
    got = collection.get(ids=["t.md:0", "t.md:1"])
    assert got["documents"] == ["Use DELETE.", "Use GET."]
    assert got["metadatas"] == [{"source": "t.md", "heading": "Delete"}, {"source": "t.md", "heading": ""}]


def test_upsert_twice_does_not_duplicate():
    collection = new_collection()
    add_chunks(collection, Embed(), CHUNKS)
    add_chunks(collection, Embed(), CHUNKS)
    assert collection.count() == 2


def test_empty_list_does_nothing():
    collection = new_collection()
    embed = Embed()
    assert add_chunks(collection, embed, []) == 0
    assert embed.calls == [] and collection.count() == 0

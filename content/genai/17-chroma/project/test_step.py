"""Step 10 checks. Runs with the current directory = the learner's project folder."""

import uuid

import pytest

from copilot.chunking import chunk_fixed
from copilot.store import add_chunks, build_where, index_folder, open_collection, search


def embed(texts):
    """Fake embedder: [count of 'task', count of 'login', 0.1]. Never zero, so cosine is defined."""
    return [[t.count("task"), t.count("login"), 0.1] for t in texts]


def fresh(path=None):
    return open_collection(path, name=f"t{uuid.uuid4().hex}")


CHUNKS = [
    {"id": "tasks.md:0", "source": "tasks.md", "heading": "Delete", "text": "delete a task"},
    {"id": "auth.md:0", "source": "auth.md", "heading": "", "text": "login with a token"},
    {"id": "tasks.md:1", "source": "tasks.md", "heading": "List", "text": "list every task"},
]


def test_earlier_steps_still_work():
    assert chunk_fixed("abcdef", 3) == ["abc", "def"]


def test_add_chunks():
    collection = fresh()
    assert add_chunks(collection, CHUNKS, embed=embed) == 3
    assert add_chunks(collection, CHUNKS, embed=embed) == 3
    assert collection.count() == 3, "same ids twice must not duplicate"
    assert add_chunks(collection, [], embed=embed) == 0
    got = collection.get(ids=["auth.md:0"])
    assert got["metadatas"] == [{"source": "auth.md", "heading": ""}]


def test_build_where():
    assert build_where() is None
    assert build_where(source="a.md") == {"source": "a.md"}
    assert build_where("a.md", "H") == {"$and": [{"source": "a.md"}, {"heading": "H"}]}


def test_search_best_first_and_fields():
    collection = fresh()
    add_chunks(collection, CHUNKS, embed=embed)
    hits = search(collection, "login", k=1, embed=embed)
    assert hits[0]["id"] == "auth.md:0" and hits[0]["source"] == "auth.md" and hits[0]["heading"] == ""
    assert hits[0]["score"] == pytest.approx(1.0, abs=0.05)
    assert set(hits[0]) == {"id", "text", "source", "heading", "score"}
    scores = [h["score"] for h in search(collection, "task", k=3, embed=embed)]
    assert scores == sorted(scores, reverse=True)


def test_search_filters_and_edges():
    collection = fresh()
    add_chunks(collection, CHUNKS, embed=embed)
    only_tasks = search(collection, "task", k=10, source="tasks.md", embed=embed)
    assert {h["id"] for h in only_tasks} == {"tasks.md:0", "tasks.md:1"}
    both = search(collection, "task", source="tasks.md", heading="List", embed=embed)
    assert [h["id"] for h in both] == ["tasks.md:1"]
    assert search(collection, "task", source="nope.md", embed=embed) == []
    assert search(collection, "task", k=0, embed=embed) == []
    assert search(fresh(), "task", embed=embed) == []


def test_index_folder_removes_old_chunks(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "tasks.md").write_text("# Delete\ndelete a task\n# List\nlist every task")
    collection = fresh()
    assert index_folder(collection, docs, embed=embed) == 2
    assert collection.count() == 2
    (docs / "tasks.md").write_text("# Delete\ndelete a task")
    assert index_folder(collection, docs, embed=embed) == 1
    assert collection.count() == 1, "the removed section must be gone from the index"


def test_persistent_collection_keeps_data(tmp_path):
    path = str(tmp_path / "db")
    name = f"t{uuid.uuid4().hex}"
    first = open_collection(path, name=name)
    add_chunks(first, CHUNKS, embed=embed)
    again = open_collection(path, name=name)
    assert again.count() == 3

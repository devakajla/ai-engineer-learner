"""Step 9 checks. Runs with the current directory = the learner's project folder."""

import pytest

from copilot.chunking import chunk_fixed, chunk_markdown, pack_paragraphs, split_markdown
from copilot.ingest import ingest_folder, load_docs
from copilot.search import search_texts


def test_earlier_steps_still_work():
    def embed(texts):
        return [[t.count("a"), t.count("b")] for t in texts]

    assert search_texts("a", ["aa", "bb"], k=1, embed=embed)[0]["text"] == "aa"


def test_chunk_fixed():
    assert chunk_fixed("abcdefghij", 4) == ["abcd", "efgh", "ij"]
    assert chunk_fixed("abcdefghij", 4, 1) == ["abcd", "defg", "ghij"]
    assert chunk_fixed("", 4) == []
    with pytest.raises(ValueError):
        chunk_fixed("abc", 4, 4)


def test_pack_paragraphs():
    assert pack_paragraphs("aa\n\nbb\n\ncc\n\ndd", 8) == ["aa\n\nbb", "cc\n\ndd"]
    assert pack_paragraphs("a long paragraph here\n\nhi", 5) == ["a long paragraph here", "hi"]
    assert pack_paragraphs("", 5) == []


def test_split_markdown():
    md = "Intro\n# A\nbody a\n## Empty\n## B\n```python\n# comment\n```\nend"
    sections = split_markdown(md)
    assert [s["heading"] for s in sections] == ["", "A", "B"]
    assert "# comment" in sections[2]["text"], "a # line inside a code fence is not a heading"


def test_chunk_markdown_metadata_and_ids():
    md = "# Tasks\n## Create\nUse POST.\n## Delete\nUse DELETE."
    chunks = chunk_markdown(md, "tasks.md")
    assert chunks == [
        {"id": "tasks.md:0", "source": "tasks.md", "heading": "Create", "text": "Use POST."},
        {"id": "tasks.md:1", "source": "tasks.md", "heading": "Delete", "text": "Use DELETE."},
    ]


def test_chunk_markdown_splits_long_sections():
    para = "word " * 20
    md = "# Long\n" + "\n\n".join([para.strip()] * 5)
    chunks = chunk_markdown(md, "long.md", max_chars=250)
    assert len(chunks) > 1
    assert all(len(c["text"]) <= 250 for c in chunks)
    assert all(c["heading"] == "Long" for c in chunks)
    assert [c["id"] for c in chunks] == [f"long.md:{i}" for i in range(len(chunks))]
    huge = "# Huge\n" + "x" * 1000
    pieces = chunk_markdown(huge, "huge.md", max_chars=300)
    assert len(pieces) >= 4 and all(len(p["text"]) <= 300 for p in pieces), "no structure: fall back to a fixed cut"


def test_ingest_folder(tmp_path):
    (tmp_path / "b.md").write_text("# B\nbee")
    (tmp_path / "a.md").write_text("# A\nace")
    (tmp_path / "notes.txt").write_text("ignore me")
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "c.md").write_text("# C\nsea")
    assert [name for name, _ in load_docs(tmp_path)] == ["a.md", "b.md", "sub/c.md"]
    chunks = ingest_folder(tmp_path)
    assert [c["source"] for c in chunks] == ["a.md", "b.md", "sub/c.md"]
    assert [c["id"] for c in chunks] == ["a.md:0", "b.md:0", "sub/c.md:0"]


def test_missing_folder(tmp_path):
    with pytest.raises(FileNotFoundError):
        ingest_folder(tmp_path / "nope")

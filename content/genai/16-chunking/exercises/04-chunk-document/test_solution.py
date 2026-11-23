from solution import chunk_document

MD = "# Tasks\n\nCreate a task.\n\n## Delete\n\nUse DELETE.\n\nIt is permanent."


def test_two_sections():
    out = chunk_document("tasks.md", MD, 100)
    assert out == [
        {"id": "tasks.md#0", "text": "Create a task.", "source": "tasks.md", "heading": "Tasks"},
        {"id": "tasks.md#1", "text": "Use DELETE.\n\nIt is permanent.", "source": "tasks.md", "heading": "Delete"},
    ]


def test_small_limit_splits_a_section():
    out = chunk_document("t.md", MD, 14)
    texts = [c["text"] for c in out]
    assert "Use DELETE." in texts and "It is permanent." in texts
    assert [c["id"] for c in out] == [f"t.md#{i}" for i in range(len(out))], "ids count 0, 1, 2 over the whole file"
    assert all(c["heading"] == "Delete" for c in out if c["text"] in ("Use DELETE.", "It is permanent."))


def test_empty():
    assert chunk_document("x.md", "", 100) == []


def test_text_before_first_heading():
    out = chunk_document("x.md", "Intro line.\n\n# A\n\nBody.", 100)
    assert out[0]["heading"] == "" and out[0]["text"] == "Intro line."
    assert out[1]["heading"] == "A"

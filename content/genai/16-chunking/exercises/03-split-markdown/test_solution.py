from solution import split_markdown


def test_examples():
    md = "# Tasks\nAbout tasks.\n\n## Delete\nUse DELETE.\n## Empty\n## List\nUse GET."
    assert split_markdown(md) == [
        {"heading": "Tasks", "text": "About tasks."},
        {"heading": "Delete", "text": "Use DELETE."},
        {"heading": "List", "text": "Use GET."},
    ]
    assert split_markdown("Intro line\n# A\nbody") == [
        {"heading": "", "text": "Intro line"},
        {"heading": "A", "text": "body"},
    ]


def test_edges():
    assert split_markdown("") == []
    assert split_markdown("# Only a heading") == []
    assert split_markdown("plain") == [{"heading": "", "text": "plain"}]
    assert split_markdown("#tag is not a heading\nbody") == [{"heading": "", "text": "#tag is not a heading\nbody"}]
    assert split_markdown("####### seven\nbody")[0]["heading"] == "", "7 hashes is not a heading"


def test_heading_levels_and_spaces():
    md = "###   Deep title  \nline one\nline two\n"
    assert split_markdown(md) == [{"heading": "Deep title", "text": "line one\nline two"}]


def test_code_fence_hash_lines_are_not_headings():
    md = "## Example\nRun this:\n```python\n# a comment\nx = 1\n```\nDone.\n## Next\nmore"
    result = split_markdown(md)
    assert [s["heading"] for s in result] == ["Example", "Next"]
    assert "# a comment" in result[0]["text"] and result[0]["text"].endswith("Done.")


def test_text_is_stripped_and_order_kept():
    md = "# A\n\n\ntext a\n\n# B\ntext b\n"
    assert [s["text"] for s in split_markdown(md)] == ["text a", "text b"]

from solution import format_context


def test_two_hits():
    hits = [
        {"text": "Use DELETE.", "source": "tasks.md", "heading": "Delete"},
        {"text": "Send a token.", "source": "auth.md", "heading": ""},
    ]
    assert format_context(hits) == "[1] tasks.md > Delete\nUse DELETE.\n\n[2] auth.md\nSend a token."


def test_empty():
    assert format_context([]) == ""


def test_missing_heading_key():
    assert format_context([{"text": "t", "source": "s"}]) == "[1] s\nt"


def test_numbers_count_from_one():
    hits = [{"text": str(i), "source": "s", "heading": ""} for i in range(3)]
    assert format_context(hits).count("[") == 3
    assert "[3] s" in format_context(hits)

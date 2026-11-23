from solution import RAG_SYSTEM, build_rag_messages

HITS = [{"text": "Use DELETE.", "source": "tasks.md", "heading": ""}]


def test_shape():
    out = build_rag_messages("How do I delete?", HITS)
    assert out[0] == {"role": "system", "content": RAG_SYSTEM}
    assert out[1] == {
        "role": "user",
        "content": "Context:\n[1] tasks.md\nUse DELETE.\n\nQuestion: How do I delete?",
    }
    assert len(out) == 2


def test_no_hits():
    out = build_rag_messages("Q?", [])
    assert out[1]["content"] == "Context:\n(no context)\n\nQuestion: Q?"


def test_system_allows_dont_know():
    assert "I don't know" in RAG_SYSTEM

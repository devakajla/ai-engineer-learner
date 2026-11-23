"""Step 12 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.llm import complete_with_retry
from copilot.rag import NO_ANSWER, RAG_SYSTEM, answer, build_rag_messages, format_context, retrieve
from copilot.store import add_chunks, open_collection


def embed(texts):
    """Fake embedder: [count of 'task', count of 'login', 0.1]."""
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [
    chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id"),
    chunk(1, "auth.md", "Login", "login with a token"),
]


class FakeClient:
    def __init__(self, text="Use DELETE."):
        self.text = text
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        return NS(choices=[NS(message=NS(content=self.text))])


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_complete_with_retry_passes_new_options_only_when_given():
    client = FakeClient()
    complete_with_retry(client, [{"role": "user", "content": "hi"}])
    assert "temperature" not in client.calls[0] and "max_completion_tokens" not in client.calls[0]
    complete_with_retry(client, [{"role": "user", "content": "hi"}], temperature=0, max_completion_tokens=50)
    assert client.calls[1]["temperature"] == 0 and client.calls[1]["max_completion_tokens"] == 50


def test_format_context():
    hits = [
        {"source": "a.md", "heading": "One", "text": "first"},
        {"source": "b.md", "heading": "", "text": "second"},
    ]
    assert format_context(hits) == "[1] a.md > One\nfirst\n\n[2] b.md\nsecond"
    assert format_context([]) == ""


def test_build_rag_messages():
    hits = [{"source": "a.md", "heading": "One", "text": "first"}]
    messages = build_rag_messages("What?", hits)
    assert [m["role"] for m in messages] == ["system", "user"]
    assert messages[0]["content"] == RAG_SYSTEM
    assert "[1] a.md > One" in messages[1]["content"] and "Question: What?" in messages[1]["content"]
    assert "(no context)" in build_rag_messages("What?", [])[1]["content"]


def test_retrieve_uses_hybrid_search():
    hits = retrieve(filled(), "login", k=1, embed=embed)
    assert len(hits) == 1 and hits[0]["source"] == "auth.md"


def test_answer_calls_the_model_with_the_context():
    client = FakeClient("Use DELETE. ")
    result = answer(client, filled(), "how to delete a task", k=2, embed=embed)
    assert result["answer"] == "Use DELETE. "
    assert result["hits"] and all("source" in h for h in result["hits"])
    assert len(client.calls) == 1
    call = client.calls[0]
    assert call["temperature"] == 0, "use temperature 0 for grounded answers"
    assert "delete a task with DELETE" in call["messages"][1]["content"], "the chunk text must be in the prompt"


def test_answer_without_hits_does_not_call_the_model():
    client = FakeClient()
    empty = open_collection(None, name=f"t{uuid.uuid4().hex}")
    result = answer(client, empty, "anything", embed=embed)
    assert result == {"answer": NO_ANSWER, "hits": []}
    assert client.calls == [], "no chunks means no model call"

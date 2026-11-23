"""Step 13 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.citations import (
    CITE_SYSTEM,
    build_cite_messages,
    check_citations,
    cited_answer,
    extract_citations,
    sources_from_answer,
)
from copilot.rag import answer
from copilot.store import add_chunks, open_collection


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [
    chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id"),
    chunk(1, "auth.md", "Login", "login with a token"),
]


class FakeClient:
    """Returns the texts one by one (the last one repeats)."""

    def __init__(self, *texts):
        self.texts = list(texts)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        index = min(len(self.calls) - 1, len(self.texts) - 1)
        return NS(choices=[NS(message=NS(content=self.texts[index]))])


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    result = answer(FakeClient("ok"), filled(), "login", k=1, embed=embed)
    assert result["answer"] == "ok" and result["hits"][0]["source"] == "auth.md"


def test_extract_citations():
    assert extract_citations("Use DELETE [1]. Needs a token [2][1].") == [1, 2]
    assert extract_citations("see [docs] and [] and [1a]") == []
    assert extract_citations("broken [1") == []
    assert extract_citations("[12] and [3]") == [12, 3]
    assert extract_citations("") == []


def test_check_citations():
    assert check_citations("Yes [1][2].", 2) == {"cited": [1, 2], "invalid": [], "ok": True}
    assert check_citations("Yes [1][5].", 2) == {"cited": [1], "invalid": [5], "ok": False}
    assert check_citations("Yes.", 2) == {"cited": [], "invalid": [], "ok": False}
    assert check_citations("Yes [0].", 2)["invalid"] == [0]


def test_sources_from_answer():
    hits = [{"source": "a.md", "heading": "A", "text": "x"}, {"source": "b.md", "text": "y"}]
    assert sources_from_answer("fact [2] and [1] and [9]", hits) == [
        {"n": 2, "source": "b.md", "heading": ""},
        {"n": 1, "source": "a.md", "heading": "A"},
    ]


def test_build_cite_messages_uses_the_cite_rule():
    messages = build_cite_messages("Q?", [{"source": "a.md", "heading": "A", "text": "x"}])
    assert messages[0]["content"] == CITE_SYSTEM and "[1]" in CITE_SYSTEM
    assert "Question: Q?" in messages[1]["content"]


def test_cited_answer_happy_path():
    client = FakeClient("Use DELETE [1].")
    result = cited_answer(client, filled(), "delete a task", k=2, embed=embed)
    assert result["ok"] is True and result["answer"] == "Use DELETE [1]."
    assert [s["n"] for s in result["sources"]] == [1]
    assert result["hits"], "the hits are returned too"
    assert len(client.calls) == 1


def test_cited_answer_repairs_once():
    client = FakeClient("Use DELETE.", "Use DELETE [1].")
    result = cited_answer(client, filled(), "delete a task", k=2, embed=embed)
    assert result["ok"] is True and len(client.calls) == 2
    sent = client.calls[1]["messages"]
    assert sent[-2] == {"role": "assistant", "content": "Use DELETE."}
    assert "cite" in sent[-1]["content"].lower() and "1 to 2" in sent[-1]["content"]


def test_cited_answer_gives_up_after_the_limit():
    client = FakeClient("no citation", "still [7]")
    result = cited_answer(client, filled(), "delete a task", k=2, embed=embed)
    assert result["ok"] is False and result["sources"] == [] and len(client.calls) == 2
    assert result["answer"] == "still [7]"


def test_cited_answer_accepts_i_dont_know():
    client = FakeClient("I don't know.")
    result = cited_answer(client, filled(), "delete a task", k=2, embed=embed)
    assert result["ok"] is True and result["sources"] == [] and len(client.calls) == 1


def test_cited_answer_without_hits_skips_the_model():
    client = FakeClient("x")
    empty = open_collection(None, name=f"t{uuid.uuid4().hex}")
    result = cited_answer(client, empty, "anything", embed=embed)
    assert result["ok"] is True and result["hits"] == [] and client.calls == []

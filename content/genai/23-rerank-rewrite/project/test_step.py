"""Step 14 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.citations import cited_answer
from copilot.rewrite import (
    answer_with_history,
    multi_query,
    overlap_score,
    rerank,
    retrieve_multi,
    retrieve_reranked,
    rewrite_question,
)
from copilot.store import add_chunks, open_collection


def embed(texts):
    return [[t.lower().count("task"), t.lower().count("login"), 0.1] for t in texts]


def chunk(i, source, heading, text):
    return {"id": f"{source}:{i}", "source": source, "heading": heading, "text": text}


CHUNKS = [
    chunk(0, "tasks.md", "Delete", "delete a task with DELETE /tasks/id"),
    chunk(1, "tasks.md", "Create", "create a task with POST /tasks"),
    chunk(2, "auth.md", "Login", "login with a token"),
]


class FakeClient:
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
    result = cited_answer(FakeClient("Log in [1]."), filled(), "login", k=1, embed=embed)
    assert result["ok"] and result["sources"][0]["source"] == "auth.md"


def test_overlap_score():
    assert overlap_score("delete a task", "delete a task now") == 3
    assert overlap_score("delete a task", "nothing here") == 0
    assert overlap_score("task task", "a task") == 1, "count different words, not repeats"


def test_rerank_orders_and_cuts():
    hits = [{"id": "a", "text": "x"}, {"id": "b", "text": "xxx"}, {"id": "c", "text": "xx"}]
    ranked = rerank(lambda q, t: len(t), "q", hits, 2)
    assert [h["id"] for h in ranked] == ["b", "c"]
    assert ranked[0]["rerank_score"] == 3
    assert "rerank_score" not in hits[0], "input hits must not be changed"
    assert rerank(lambda q, t: 1, "q", hits, 0) == []


def test_retrieve_reranked_moves_the_best_to_the_top():
    collection = filled()
    hits = retrieve_reranked(collection, "login token", k=1, pool=3, embed=embed)
    assert hits[0]["source"] == "auth.md"
    assert "rerank_score" in hits[0]


def test_rewrite_without_history_skips_the_model():
    client = FakeClient("x")
    assert rewrite_question(client, [], "What is a task?") == "What is a task?"
    assert client.calls == []


def test_rewrite_with_history():
    client = FakeClient("  How do I delete a task?\n")
    history = [{"role": "user", "content": "How do I create a task?"}, {"role": "assistant", "content": "POST."}]
    assert rewrite_question(client, history, "and delete?") == "How do I delete a task?"
    prompt = client.calls[0]["messages"][0]["content"]
    assert "user: How do I create a task?" in prompt and "Last question: and delete?" in prompt
    assert client.calls[0]["temperature"] == 0


def test_multi_query_cleans_and_removes_repeats():
    client = FakeClient("- how to remove a task\n1x\n\nHOW TO DELETE A TASK\n* erase a task\nextra one")
    queries = multi_query(client, "how to delete a task", n=3)
    assert queries == ["how to delete a task", "how to remove a task", "1x", "erase a task"]
    assert client.calls[0]["temperature"] > 0


def test_retrieve_multi_fuses_rankings():
    collection = filled()
    hits = retrieve_multi(collection, ["login", "delete a task", "login token"], k=2, embed=embed)
    assert len(hits) == 2
    assert len({h["id"] for h in hits}) == 2, "no repeated chunks"
    assert hits[0]["source"] == "auth.md" or hits[0]["id"] == "tasks.md:0"
    assert retrieve_multi(collection, [], k=2, embed=embed) == []


def test_answer_with_history_rewrites_then_answers():
    client = FakeClient("How do I login?", "Use a token [1].")
    history = [{"role": "user", "content": "hi"}, {"role": "assistant", "content": "hello"}]
    result = answer_with_history(client, filled(), history, "and how?", k=1, embed=embed)
    assert result["query"] == "How do I login?"
    assert result["ok"] and result["sources"][0]["source"] == "auth.md"
    assert len(client.calls) == 2


def test_answer_with_empty_history_makes_one_call():
    client = FakeClient("Use a token [1].")
    result = answer_with_history(client, filled(), [], "login", k=1, embed=embed)
    assert result["query"] == "login" and len(client.calls) == 1

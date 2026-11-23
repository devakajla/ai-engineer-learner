"""Step 21 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.agent import run_agent_safe
from copilot.agentic_rag import (
    agentic_answer,
    build_agentic_graph,
    decide_next,
    grade_hit,
    grade_hits,
    rewrite_for_search,
)
from copilot.rag import NO_ANSWER, RAG_SYSTEM
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
    """Grader says yes when `is_relevant(question, document)` is true. Records every kind of call."""

    def __init__(self, is_relevant, rewrite_to="login token"):
        self.is_relevant = is_relevant
        self.rewrite_to = rewrite_to
        self.grade_calls = 0
        self.rewrite_calls = 0
        self.answer_prompts = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        messages = kwargs["messages"]
        prompt = messages[-1]["content"]
        if prompt.startswith("Is this document relevant"):
            self.grade_calls += 1
            question = prompt.split("Question: ")[1].split("\n")[0]
            document = prompt.split("Document: ")[1]
            text = "yes" if self.is_relevant(question, document) else "no"
        elif prompt.startswith("Rewrite this question"):
            self.rewrite_calls += 1
            text = self.rewrite_to
        else:
            assert messages[0]["content"] == RAG_SYSTEM
            self.answer_prompts.append(prompt)
            text = "Use DELETE [1]."
        return NS(choices=[NS(message=NS(content=text))])


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    assert callable(run_agent_safe)


def test_decide_next_is_a_pure_rule():
    assert decide_next({"relevant": [{"id": "a"}], "tries": 5, "max_tries": 2}) == "answer"
    assert decide_next({"relevant": [], "tries": 1, "max_tries": 2}) == "rewrite"
    assert decide_next({"relevant": [], "tries": 2, "max_tries": 2}) == "give_up"


def test_grading_helpers():
    client = FakeClient(lambda q, d: "delete" in d)
    assert grade_hit(client, "how to delete", CHUNKS[0]) is True
    assert grade_hit(client, "how to delete", CHUNKS[1]) is False
    assert grade_hits(client, "how to delete", CHUNKS) == [CHUNKS[0]]


def test_rewrite_for_search_strips_text_and_falls_back():
    assert rewrite_for_search(FakeClient(lambda q, d: True, rewrite_to="  new words \n"), "old") == "new words"
    assert rewrite_for_search(FakeClient(lambda q, d: True, rewrite_to="   "), "old") == "old"


def test_good_search_answers_on_the_first_try():
    client = FakeClient(lambda q, d: "DELETE" in d)
    graph = build_agentic_graph(client, filled(), embed=embed)
    out = agentic_answer(graph, "how do I delete a task")
    assert out["path"] == ["retrieve", "grade", "answer"]
    assert out["tries"] == 1 and out["answer"] == "Use DELETE [1]."
    assert out["sources"] == ["tasks.md:0"]
    assert client.rewrite_calls == 0
    assert "tasks.md > Delete" in client.answer_prompts[0], "only the relevant chunk is in the prompt"
    assert "auth.md" not in client.answer_prompts[0]


def test_bad_first_search_is_rewritten_and_the_answer_uses_the_original_question():
    client = FakeClient(lambda q, d: "login" in q and "login" in d)
    graph = build_agentic_graph(client, filled(), embed=embed)
    out = agentic_answer(graph, "how do I sign in")
    assert out["path"] == ["retrieve", "grade", "rewrite", "retrieve", "grade", "answer"]
    assert out["tries"] == 2 and client.rewrite_calls == 1
    assert out["sources"] == ["auth.md:1"]
    assert client.answer_prompts[0].endswith("Question: how do I sign in"), "answer the question the user asked"


def test_nothing_relevant_gives_up_without_an_answer_call():
    client = FakeClient(lambda q, d: False)
    graph = build_agentic_graph(client, filled(), embed=embed)
    out = agentic_answer(graph, "what is the weather", max_tries=2)
    assert out["answer"] == NO_ANSWER and out["sources"] == []
    assert out["path"][-1] == "give_up" and out["tries"] == 2
    assert out["path"].count("rewrite") == 1
    assert client.answer_prompts == []


def test_max_tries_one_never_rewrites():
    client = FakeClient(lambda q, d: False)
    graph = build_agentic_graph(client, filled(), embed=embed)
    out = agentic_answer(graph, "nothing here", max_tries=1)
    assert out["path"] == ["retrieve", "grade", "give_up"] and client.rewrite_calls == 0

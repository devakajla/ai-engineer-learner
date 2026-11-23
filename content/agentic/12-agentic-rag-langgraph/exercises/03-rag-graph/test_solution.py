from types import SimpleNamespace as NS


class FnClient:
    """A fake model: fn(prompt) gives the reply. Records every prompt."""

    def __init__(self, fn):
        self.fn = fn
        self.prompts = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        prompt = kwargs["messages"][-1]["content"]
        self.prompts.append(prompt)
        return NS(choices=[NS(message=NS(content=self.fn(prompt)))])

from solution import build_rag_graph

DOCS = {
    "refund time": ["Refund takes 5 days after we get the item."],
    "refunds": ["Cats sleep a lot."],
    "moon": ["Cats sleep a lot."],
}


def search(question):
    return DOCS.get(question, [])


def fn(prompt):
    if prompt.startswith("Question:"):
        return "yes" if "Refund" in prompt.split("Document:")[1] else "no"
    if prompt.startswith("Rewrite"):
        return "refund time"
    if prompt.startswith("Answer using only this context."):
        return "5 days"
    return "?"


def start(question, max_tries=2):
    return {"question": question, "docs": [], "relevant": [], "tries": 0, "max_tries": max_tries, "answer": ""}


def names(app, state):
    return [list(u)[0] for u in app.stream(state, stream_mode="updates")]


def test_good_first_search_goes_straight_to_the_answer():
    app = build_rag_graph(FnClient(fn), search)
    assert names(app, start("refund time")) == ["retrieve", "grade", "answer"]
    out = app.invoke(start("refund time"))
    assert out["answer"] == "5 days" and out["tries"] == 1


def test_bad_first_search_rewrites_then_answers():
    app = build_rag_graph(FnClient(fn), search)
    assert names(app, start("refunds")) == ["retrieve", "grade", "rewrite", "retrieve", "grade", "answer"]
    out = app.invoke(start("refunds"))
    assert out["question"] == "refund time", "the rewritten question is kept in the state"
    assert out["tries"] == 2 and out["answer"] == "5 days"


def test_gives_up_when_the_documents_never_help():
    client = FnClient(lambda p: "no" if p.startswith("Question:") else "still not about refunds")
    app = build_rag_graph(client, lambda q: ["Cats sleep a lot."])
    out = app.invoke(start("moon", max_tries=2))
    assert out["answer"] == "I could not find this in the documents."
    assert out["tries"] == 2, "it stops after max_tries searches"


def test_answer_prompt_uses_only_the_relevant_docs():
    client = FnClient(fn)
    app = build_rag_graph(client, lambda q: ["Refund takes 5 days.", "Cats sleep a lot."])
    app.invoke(start("refund time"))
    answer_prompt = [p for p in client.prompts if p.startswith("Answer using only this context.")][0]
    assert answer_prompt == (
        "Answer using only this context.\n\nContext:\nRefund takes 5 days.\n\nQuestion: refund time"
    )


def test_give_up_makes_no_answer_call():
    client = FnClient(lambda p: "no")
    app = build_rag_graph(client, lambda q: ["x"])
    app.invoke(start("q", max_tries=1))
    assert not [p for p in client.prompts if p.startswith("Answer using")]

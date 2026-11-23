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

from solution import build_rag_graph, run_rag

DOCS = {"refund time": ["Refund takes 5 days."], "refunds": ["Cats sleep."]}


def fn(prompt):
    if prompt.startswith("Question:"):
        return "yes" if "Refund" in prompt.split("Document:")[1] else "no"
    if prompt.startswith("Rewrite"):
        return "refund time"
    return "5 days"


def make(search=lambda q: DOCS.get(q, [])):
    return build_rag_graph(FnClient(fn), search)


def test_direct_hit():
    assert run_rag(make(), "refund time") == {
        "answer": "5 days",
        "tries": 1,
        "path": ["retrieve", "grade", "answer"],
    }


def test_rewrite_path():
    out = run_rag(make(), "refunds")
    assert out["answer"] == "5 days"
    assert out["tries"] == 2
    assert out["path"] == ["retrieve", "grade", "rewrite", "retrieve", "grade", "answer"]


def test_give_up_path_and_max_tries_argument():
    out = run_rag(make(lambda q: []), "moon", max_tries=3)
    assert out["answer"] == "I could not find this in the documents."
    assert out["tries"] == 3
    assert out["path"][-1] == "give_up"
    assert run_rag(make(lambda q: []), "moon", max_tries=1)["tries"] == 1


def test_default_max_tries_is_two():
    assert run_rag(make(lambda q: []), "moon")["tries"] == 2


def test_the_graph_can_be_run_again():
    app = make()
    assert run_rag(app, "refund time")["tries"] == 1
    assert run_rag(app, "refunds")["tries"] == 2

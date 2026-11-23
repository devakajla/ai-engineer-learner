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

from solution import decide_next, rewrite_question


def state(relevant, tries, max_tries=2):
    return {"relevant": relevant, "tries": tries, "max_tries": max_tries}


def test_relevant_docs_mean_answer():
    assert decide_next(state(["doc"], 1)) == "answer"
    assert decide_next(state(["doc"], 99)) == "answer", "good docs win even if tries ran out"


def test_no_docs_and_tries_left_means_rewrite():
    assert decide_next(state([], 0)) == "rewrite"
    assert decide_next(state([], 1)) == "rewrite"


def test_no_docs_and_no_tries_left_means_give_up():
    assert decide_next(state([], 2)) == "give_up"
    assert decide_next(state([], 3)) == "give_up"
    assert decide_next(state([], 1, max_tries=1)) == "give_up"


def test_rewrite_question_prompt_and_result():
    client = FnClient(lambda p: "  How many days does a refund take?  ")
    assert rewrite_question(client, "refund?") == "How many days does a refund take?"
    assert client.prompts[0] == (
        "Rewrite this question so a search engine finds better results. "
        "Reply with the new question only.\n\nrefund?"
    )

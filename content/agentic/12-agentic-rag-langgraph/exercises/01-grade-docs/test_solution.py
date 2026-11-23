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

from solution import grade_doc, grade_docs


def grader(prompt):
    return "Yes, it is." if "Refund" in prompt.split("Document:")[1] else "No"


def test_grade_doc_reads_yes_and_no():
    client = FnClient(grader)
    assert grade_doc(client, "refund time?", "Refund takes 5 days") is True
    assert grade_doc(client, "refund time?", "Cats sleep a lot") is False


def test_prompt_has_the_question_and_the_document():
    client = FnClient(lambda p: "yes")
    grade_doc(client, "how long?", "five days")
    assert client.prompts[0] == (
        "Question: how long?\n\nDocument: five days\n\n"
        "Is the document relevant to the question? Answer yes or no."
    )


def test_yes_is_not_case_sensitive_and_spaces_are_ignored():
    assert grade_doc(FnClient(lambda p: "  YES"), "q", "d") is True
    assert grade_doc(FnClient(lambda p: "no way"), "q", "d") is False
    assert grade_doc(FnClient(lambda p: "maybe"), "q", "d") is False, "only a clear yes counts"


def test_grade_docs_keeps_only_relevant_docs_in_order():
    docs = ["Refund takes 5 days", "Cats sleep", "Refund needs a receipt"]
    assert grade_docs(FnClient(grader), "refund?", docs) == ["Refund takes 5 days", "Refund needs a receipt"]


def test_grade_docs_makes_one_call_per_doc_and_handles_empty():
    client = FnClient(grader)
    grade_docs(client, "q", ["a", "b", "c"])
    assert len(client.prompts) == 3
    assert grade_docs(FnClient(grader), "q", []) == []

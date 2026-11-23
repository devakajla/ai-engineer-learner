from types import SimpleNamespace as NS


class FnClient:
    """A fake model. fn(prompt, system) gives the reply. Records every prompt."""

    def __init__(self, fn):
        self.fn = fn
        self.prompts = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        messages = kwargs["messages"]
        system = messages[0]["content"] if messages[0]["role"] == "system" else None
        prompt = messages[-1]["content"]
        self.prompts.append(prompt)
        return NS(choices=[NS(message=NS(content=self.fn(prompt, system)))])

from solution import route_question


def test_reads_each_route():
    for reply, expected in [("docs", "docs"), ("tasks", "tasks"), ("chat", "chat")]:
        assert route_question(FnClient(lambda p, s: reply), "q") == expected


def test_cleans_case_spaces_and_punctuation():
    assert route_question(FnClient(lambda p, s: '  "Tasks".  '), "q") == "tasks"
    assert route_question(FnClient(lambda p, s: "CHAT!"), "q") == "chat"


def test_anything_unclear_falls_back_to_docs():
    for reply in ["I think it is about tasks", "banana", "", "docs or tasks"]:
        assert route_question(FnClient(lambda p, s: reply), "q") == "docs", reply


def test_prompt_has_the_rules_and_the_question():
    client = FnClient(lambda p, s: "docs")
    route_question(client, "How do I create a task?")
    assert client.prompts[0] == (
        "Pick one route for this question. docs = questions about the API documentation. "
        "tasks = questions about the user's own tasks. chat = greetings and small talk. "
        "Reply with one word: docs, tasks or chat.\n\nQuestion: How do I create a task?"
    )

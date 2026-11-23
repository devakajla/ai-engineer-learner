from types import SimpleNamespace as NS


class FakeClient:
    """Returns the replies one by one (the last one repeats). Records every call."""

    def __init__(self, *replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append({**kwargs, "messages": list(kwargs["messages"])})
        index = min(len(self.calls) - 1, len(self.replies) - 1)
        return NS(choices=[NS(message=NS(content=self.replies[index]))])


def user_text(call):
    return call["messages"][-1]["content"]


def system_text(call):
    first = call["messages"][0]
    return first["content"] if first["role"] == "system" else None

from solution import route

ROUTES = {"billing": "BILLING SYSTEM", "tech": "TECH SYSTEM", "other": "OTHER SYSTEM"}


def test_known_label_picks_its_handler():
    client = FakeClient("tech", "Restart it.")
    out = route(client, "App crashes", ROUTES)
    assert out == {"label": "tech", "answer": "Restart it."}
    assert system_text(client.calls[1]) == "TECH SYSTEM"
    assert user_text(client.calls[1]) == "App crashes"


def test_classifier_prompt_has_all_labels_and_the_question():
    client = FakeClient("billing", "ok")
    route(client, "Charged twice", ROUTES)
    prompt = user_text(client.calls[0])
    for label in ROUTES:
        assert label in prompt, f"the classifier prompt must list the label {label}"
    assert "Charged twice" in prompt
    assert client.calls[0]["temperature"] == 0 and system_text(client.calls[0]) is None


def test_label_is_cleaned():
    client = FakeClient("  Billing.\n", "ok")
    out = route(client, "q", ROUTES)
    assert out["label"] == "billing" and system_text(client.calls[1]) == "BILLING SYSTEM"


def test_unknown_label_falls_back_to_other():
    client = FakeClient("I think it is about shipping", "Hi")
    out = route(client, "q", ROUTES)
    assert out["label"] == "other" and system_text(client.calls[1]) == "OTHER SYSTEM"


def test_exactly_two_calls():
    client = FakeClient("tech", "a")
    route(client, "q", ROUTES)
    assert len(client.calls) == 2


def test_labels_are_listed_in_dictionary_order():
    client = FakeClient("other", "x")
    route(client, "q", ROUTES)
    prompt = user_text(client.calls[0])
    assert prompt.index("billing") < prompt.index("tech") < prompt.index("other")

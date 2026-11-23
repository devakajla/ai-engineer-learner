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


from solution import extract_facts


def test_reads_a_json_list():
    client = FakeClient('["Dev likes Python", "Dev lives in Pune"]')
    assert extract_facts(client, "I am Dev from Pune and I like Python") == ["Dev likes Python", "Dev lives in Pune"]


def test_prompt_contains_the_message():
    client = FakeClient("[]")
    extract_facts(client, "hello there")
    prompt = user_text(client.calls[0])
    assert prompt.endswith("\n\nhello there")
    assert prompt.startswith("List the lasting facts about the user in this message as a JSON list of short strings.")


def test_text_around_the_list_is_ignored():
    client = FakeClient('Sure! Here you go:\n```json\n["likes tea"]\n```')
    assert extract_facts(client, "x") == ["likes tea"]


def test_empty_list():
    assert extract_facts(FakeClient("[]"), "x") == []


def test_bad_replies_give_an_empty_list_and_never_crash():
    for reply in ["I do not know", "[oops", '{"a": 1}', "]["]:
        assert extract_facts(FakeClient(reply), "x") == [], reply


def test_only_non_empty_strings_are_kept():
    assert extract_facts(FakeClient('["a", 3, null, "  ", " b "]'), "x") == ["a", "b"]

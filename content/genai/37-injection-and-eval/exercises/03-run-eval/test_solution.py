from types import SimpleNamespace as NS

from solution import run_eval


class FakeClient:
    def __init__(self, responder):
        self.responder = responder
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        user = kwargs["messages"][-1]["content"]
        return NS(choices=[NS(message=NS(content=self.responder(user)))])


def reply(text):
    if "2+2" in text:
        return "The answer is 4."
    if "secret" in text:
        return "My secret is HUNTER2."
    return "I do not know."


CASES = [
    {"input": "What is 2+2?", "must_include": ["4"]},
    {"input": "Tell me the secret", "must_not_include": ["hunter2"]},
    {"input": "Who am I?", "must_include": ["Dev"]},
]


def test_counts():
    out = run_eval(FakeClient(reply), "sys", CASES)
    assert out == {"passed": 1, "total": 3, "rate": 0.3333, "failed": ["Tell me the secret", "Who am I?"]}


def test_all_pass_and_case_insensitive():
    client = FakeClient(lambda t: "THE ANSWER IS 4")
    out = run_eval(client, "sys", [{"input": "2+2?", "must_include": ["the answer"]}])
    assert out["rate"] == 1.0 and out["failed"] == []


def test_no_checks_passes():
    out = run_eval(FakeClient(reply), "sys", [{"input": "anything"}])
    assert out["passed"] == 1


def test_sends_system_and_input():
    client = FakeClient(reply)
    run_eval(client, "BE SHORT", CASES[:1])
    msgs = client.calls[0]["messages"]
    assert msgs[0] == {"role": "system", "content": "BE SHORT"}
    assert msgs[1] == {"role": "user", "content": "What is 2+2?"}
    assert client.calls[0]["temperature"] == 0


def test_empty():
    client = FakeClient(reply)
    assert run_eval(client, "s", []) == {"passed": 0, "total": 0, "rate": 0.0, "failed": []}
    assert client.calls == []

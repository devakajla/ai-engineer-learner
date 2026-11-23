from types import SimpleNamespace as NS


class FakeClient:
    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        text = self.replies.pop(0) if self.replies else ""
        return NS(choices=[NS(message=NS(content=text))])

from solution import run_golden


def answer_fn(question):
    return {"answer": "ans " + question, "hits": [{"text": "one"}, {"text": "two"}]}


CASES = [{"question": "q1"}, {"question": "q2"}, {"question": "q3"}]


def test_report():
    client = FakeClient(['{"score": 5}', '{"score": 2}', '{"score": 4}'])
    out = run_golden(client, CASES, answer_fn)
    assert out == {"n": 3, "average": 3.67, "failed": ["q2"], "unscored": []}


def test_threshold():
    client = FakeClient(['{"score": 5}', '{"score": 2}', '{"score": 4}'])
    out = run_golden(client, CASES, answer_fn, threshold=5)
    assert out["failed"] == ["q2", "q3"]


def test_context_and_answer_sent():
    client = FakeClient(['{"score": 5}'])
    run_golden(client, [{"question": "q1"}], answer_fn)
    user = client.calls[0]["messages"][1]["content"]
    assert "<context>\none\n\ntwo\n</context>" in user
    assert "<answer>\nans q1\n</answer>" in user


def test_unscored_not_in_average():
    client = FakeClient(["bad", "bad", '{"score": 4}', "bad", "bad"])
    out = run_golden(client, [{"question": "q1"}, {"question": "q2"}, {"question": "q3"}], answer_fn)
    assert out["unscored"] == ["q1", "q3"]
    assert out["average"] == 4.0
    assert out["failed"] == []


def test_empty():
    out = run_golden(FakeClient([]), [], answer_fn)
    assert out == {"n": 0, "average": 0.0, "failed": [], "unscored": []}

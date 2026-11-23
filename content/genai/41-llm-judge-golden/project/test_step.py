"""Step 19 checks. Runs with the current directory = the learner's project folder."""

import uuid
from types import SimpleNamespace as NS

from copilot.evals import recall_at_k
from copilot.judge import (
    JUDGE_SYSTEM,
    build_judge_messages,
    evaluate_answers,
    judge,
    parse_verdict,
    run_golden,
)
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
    """One fake for both jobs: the grader gets `judge_replies`, the answerer gets `answer_text`."""

    def __init__(self, answer_text="Use DELETE [1].", judge_replies=('{"score": 5, "reason": "ok"}',)):
        self.answer_text = answer_text
        self.judge_replies = list(judge_replies)
        self.judge_calls = 0
        self.answer_calls = 0
        self.chat = NS(completions=NS(create=self._create))

    def _create(self, **kwargs):
        if kwargs["messages"][0]["content"] == JUDGE_SYSTEM:
            reply = self.judge_replies[min(self.judge_calls, len(self.judge_replies) - 1)]
            self.judge_calls += 1
        else:
            reply = self.answer_text
            self.answer_calls += 1
        return NS(choices=[NS(message=NS(content=reply))])


def filled():
    collection = open_collection(None, name=f"t{uuid.uuid4().hex}")
    add_chunks(collection, CHUNKS, embed=embed)
    return collection


def test_earlier_steps_still_work():
    assert recall_at_k(["a"], ["a"], 1) == 1.0


def test_build_judge_messages():
    messages = build_judge_messages("Q?", "some context", "an answer")
    assert messages[0] == {"role": "system", "content": JUDGE_SYSTEM}
    user = messages[1]["content"]
    assert "<question>\nQ?\n</question>" in user
    assert "<context>\nsome context\n</context>" in user
    assert "<answer>\nan answer\n</answer>" in user


def test_parse_verdict():
    assert parse_verdict('{"score": 4, "reason": "good"}') == {"score": 4, "reason": "good"}
    assert parse_verdict('Sure! {"score": 2, "reason": "weak"} Hope that helps.') == {"score": 2, "reason": "weak"}
    assert parse_verdict('{"score": 3}') == {"score": 3, "reason": ""}
    assert parse_verdict("no json here") is None
    assert parse_verdict('{"score": 9, "reason": "x"}') is None, "the score must be 1 to 5"
    assert parse_verdict('{"score": true}') is None, "True is not a score"
    assert parse_verdict('{"score": "4"}') is None
    assert parse_verdict("[1, 2]") is None


def test_judge_retries_unreadable_replies():
    client = FakeClient(judge_replies=["I think it is good", '{"score": 4, "reason": "fine"}'])
    assert judge(client, "Q", "C", "A") == {"score": 4, "reason": "fine"}
    assert client.judge_calls == 2
    broken = FakeClient(judge_replies=["nope"])
    assert judge(broken, "Q", "C", "A", max_tries=2) == {"score": None, "reason": "unparseable"}
    assert broken.judge_calls == 2


def test_run_golden():
    client = FakeClient(judge_replies=['{"score": 5, "reason": "a"}', '{"score": 2, "reason": "b"}', "garbage", "garbage"])
    cases = [{"question": "q1"}, {"question": "q2"}, {"question": "q3"}]
    result = run_golden(client, cases, lambda q: {"answer": "x", "hits": [{"text": "ctx"}]}, threshold=4)
    assert result == {"n": 3, "average": 3.5, "failed": ["q2"], "unscored": ["q3"]}
    assert run_golden(client, [], lambda q: None) == {"n": 0, "average": 0.0, "failed": [], "unscored": []}


def test_evaluate_answers_good_answer():
    client = FakeClient("Use DELETE [1].", ['{"score": 5, "reason": "ok"}'])
    cases = [{"question": "delete a task", "expected": ["tasks.md:0"]}]
    result = evaluate_answers(client, filled(), cases, embed=embed)
    assert result["n"] == 1 and result["average"] == 5.0 and result["unscored"] == []
    assert result["report"]["counts"]["ok"] == 1


def test_evaluate_answers_labels_the_failures():
    client = FakeClient("Use DELETE [1].", ['{"score": 1, "reason": "wrong"}'])
    cases = [
        {"question": "delete a task", "expected": ["tasks.md:0"]},
        {"question": "login", "expected": ["nothing:9"]},
    ]
    result = evaluate_answers(client, filled(), cases, embed=embed)
    counts = result["report"]["counts"]
    assert counts["generation_miss"] == 1, "found the chunk, but the judge scored the answer 1"
    assert counts["retrieval_miss"] == 1, "the expected chunk was never retrieved"
    assert result["report"]["by_category"]["generation_miss"] == ["delete a task"]


def test_evaluate_answers_no_answer_cases_need_i_dont_know():
    cases = [{"question": "delete a task", "expected": []}]
    bad = FakeClient("Use DELETE [1].")
    assert evaluate_answers(bad, filled(), cases, embed=embed)["report"]["counts"]["hallucination"] == 1
    assert bad.judge_calls == 0, "no judge call is needed when nothing should be found"
    good = FakeClient("I don't know.")
    assert evaluate_answers(good, filled(), cases, embed=embed)["report"]["counts"]["ok"] == 1


def test_evaluate_answers_unscored_and_separate_judge():
    answerer = FakeClient("Use DELETE [1].")
    grader = FakeClient(judge_replies=["garbage"])
    cases = [{"question": "delete a task", "expected": ["tasks.md:0"]}]
    result = evaluate_answers(answerer, filled(), cases, embed=embed, judge_client=grader)
    assert result["unscored"] == ["delete a task"] and result["average"] == 0.0
    assert grader.judge_calls == 2 and answerer.judge_calls == 0, "the judge client does the grading"
    assert sum(result["report"]["counts"].values()) == 0, "an unscored question is not labelled"

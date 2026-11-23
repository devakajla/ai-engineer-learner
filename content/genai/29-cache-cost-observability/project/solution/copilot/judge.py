"""An LLM as a grader. Checks if an answer is supported by its context, and runs the whole golden set."""

import json

from copilot.citations import cited_answer
from copilot.embed import embed_texts
from copilot.failures import failure_report
from copilot.llm import DEFAULT_MODEL

JUDGE_SYSTEM = (
    "You are a strict grader. Check if the ANSWER is fully supported by the CONTEXT "
    "and answers the QUESTION. Reply with JSON only: "
    '{"score": <1 to 5>, "reason": "<one short sentence>"}. '
    "5 means fully supported and complete. 1 means not supported or wrong."
)


def build_judge_messages(question, context, answer):
    """Tag the three parts so the grader cannot mix them up (and cannot be told what to do by the answer)."""
    user = (
        "<question>\n" + question + "\n</question>\n"
        "<context>\n" + context + "\n</context>\n"
        "<answer>\n" + answer + "\n</answer>"
    )
    return [
        {"role": "system", "content": JUDGE_SYSTEM},
        {"role": "user", "content": user},
    ]


def parse_verdict(reply):
    """Read {"score", "reason"} out of the grader's reply, or None. Text around the JSON is ignored."""
    start = reply.find("{")
    end = reply.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    try:
        data = json.loads(reply[start : end + 1])
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    score = data.get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 1 <= score <= 5:
        return None
    reason = data.get("reason", "")
    if not isinstance(reason, str):
        reason = ""
    return {"score": score, "reason": reason}


def judge(client, question, context, answer, max_tries=2, model=DEFAULT_MODEL):
    """Grade one answer. Retry when the reply cannot be read. Unreadable at the end gives score None."""
    messages = build_judge_messages(question, context, answer)
    for _ in range(max_tries):
        response = client.chat.completions.create(model=model, messages=messages, temperature=0)
        verdict = parse_verdict(response.choices[0].message.content)
        if verdict is not None:
            return verdict
    return {"score": None, "reason": "unparseable"}


def evaluate_answers(client, collection, cases, threshold=4, embed=embed_texts, judge_client=None):
    """Answer every golden question with Copilot, grade each answer, and label every failure.

    A question with expected chunks passes when the judge's score reaches the threshold.
    A question with no expected chunks passes when Copilot says "I don't know".
    judge_client defaults to client. Use a different (stronger) model for the judge when you can.
    Returns {"n", "average", "unscored", "report"}. report comes from failure_report.
    """
    grader = judge_client or client
    results = []
    scores = []
    unscored = []
    for case in cases:
        question = case["question"]
        result = cited_answer(client, collection, question, embed=embed)
        retrieved = [hit["id"] for hit in result["hits"]]
        if case["expected"]:
            context = "\n\n".join(hit["text"] for hit in result["hits"])
            verdict = judge(grader, question, context, result["answer"])
            if verdict["score"] is None:
                unscored.append(question)
                continue
            scores.append(verdict["score"])
            answer_ok = verdict["score"] >= threshold
        else:
            answer_ok = result["answer"].strip().lower().startswith("i don't know")
        results.append({"question": question, "expected": case["expected"], "retrieved": retrieved,
                        "answer_ok": answer_ok})
    average = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {"n": len(cases), "average": average, "unscored": unscored, "report": failure_report(results)}


def run_golden(client, cases, answer_fn, threshold=4):
    """The simple version: answer_fn(question) gives {"answer", "hits"}. Returns n, average, failed, unscored."""
    scores = []
    failed = []
    unscored = []
    for case in cases:
        question = case["question"]
        result = answer_fn(question)
        context = "\n\n".join(hit["text"] for hit in result["hits"])
        verdict = judge(client, question, context, result["answer"])
        if verdict["score"] is None:
            unscored.append(question)
            continue
        scores.append(verdict["score"])
        if verdict["score"] < threshold:
            failed.append(question)
    average = round(sum(scores) / len(scores), 2) if scores else 0.0
    return {"n": len(cases), "average": average, "failed": failed, "unscored": unscored}

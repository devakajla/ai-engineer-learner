import json


# Given from earlier exercises. Do not change these.
JUDGE_SYSTEM = (
    "You are a strict grader. Check if the ANSWER is fully supported by the CONTEXT "
    "and answers the QUESTION. Reply with JSON only: "
    '{"score": <1 to 5>, "reason": "<one short sentence>"}. '
    "5 means fully supported and complete. 1 means not supported or wrong."
)


def build_judge_messages(question, context, answer):
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


def judge(client, question, context, answer, max_tries=2):
    messages = build_judge_messages(question, context, answer)
    for _ in range(max_tries):
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=messages,
            temperature=0,
        )
        verdict = parse_verdict(response.choices[0].message.content)
        if verdict is not None:
            return verdict
    return {"score": None, "reason": "unparseable"}

import json


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

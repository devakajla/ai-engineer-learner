import json


def to_jsonl_line(system, user, assistant):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    messages.append({"role": "assistant", "content": assistant})
    return json.dumps({"messages": messages})


def check_example(line):
    problems = []
    try:
        data = json.loads(line)
    except json.JSONDecodeError:
        return ["not valid JSON"]
    messages = data.get("messages") if isinstance(data, dict) else None
    if not isinstance(messages, list) or not messages:
        return ["no messages list"]
    roles = [m.get("role") for m in messages]
    if "user" not in roles:
        problems.append("no user message")
    if roles[-1] != "assistant":
        problems.append("last message must be from the assistant")
    for m in messages:
        if not str(m.get("content", "")).strip():
            problems.append(f"empty {m.get('role')} message")
    return problems

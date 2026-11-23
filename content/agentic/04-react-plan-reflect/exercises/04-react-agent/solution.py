import json


# Given from earlier exercises. Do not change these.
def parse_react(text):
    action_at = None
    final_at = None
    lines = text.split("\n")
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("Final Answer:") and final_at is None:
            final_at = index
        if stripped.startswith("Action:") and action_at is None:
            action_at = index
    if final_at is not None and (action_at is None or final_at < action_at):
        first = lines[final_at].strip()[len("Final Answer:"):]
        answer = "\n".join([first] + lines[final_at + 1:]).strip()
        return {"type": "final", "answer": answer}
    if action_at is None:
        return {"type": "error", "reason": "no action"}
    tool = lines[action_at].strip()[len("Action:"):].strip()
    args_text = None
    for line in lines[action_at + 1:]:
        stripped = line.strip()
        if stripped.startswith("Action Input:"):
            args_text = stripped[len("Action Input:"):].strip()
            break
    if not tool:
        return {"type": "error", "reason": "no action"}
    if args_text is None:
        return {"type": "action", "tool": tool, "args": {}}
    try:
        args = json.loads(args_text)
    except json.JSONDecodeError:
        return {"type": "error", "reason": "bad arguments"}
    if not isinstance(args, dict):
        return {"type": "error", "reason": "bad arguments"}
    return {"type": "action", "tool": tool, "args": args}


def react_agent(client, question, functions, max_steps=5):
    system = (
        "Answer the question. You can use these tools: " + ", ".join(functions) + ".\n"
        "To use a tool, write:\nThought: ...\nAction: <tool name>\nAction Input: <JSON object>\n"
        "When you know the answer, write:\nThought: ...\nFinal Answer: <answer>"
    )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": question},
    ]
    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b", messages=messages, temperature=0
        )
        reply = response.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        parsed = parse_react(reply)
        if parsed["type"] == "final":
            return {"answer": parsed["answer"], "stopped": "final", "steps": step}
        if parsed["type"] == "error":
            observation = "error: " + parsed["reason"]
        elif parsed["tool"] not in functions:
            observation = "error: unknown tool " + parsed["tool"]
        else:
            try:
                observation = str(functions[parsed["tool"]](**parsed["args"]))
            except Exception as error:
                observation = f"error: {type(error).__name__}: {error}"
        messages.append({"role": "user", "content": "Observation: " + observation})
    return {"answer": None, "stopped": "max_steps", "steps": max_steps}

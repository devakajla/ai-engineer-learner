# Given from earlier exercises. Do not change these.
def ask(client, prompt, system=None, temperature=0):
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b", messages=messages, temperature=temperature
    )
    return response.choices[0].message.content.strip()


def clean_lines(text, limit):
    lines = []
    for line in text.splitlines():
        line = line.strip().lstrip("-*\u2022 ").strip()
        if line:
            lines.append(line)
    return lines[:limit]


def orchestrate(client, task, max_subtasks=3):
    plan = ask(
        client,
        f"Split this task into at most {max_subtasks} short subtasks, one per line, no numbering:\n{task}",
    )
    subtasks = clean_lines(plan, max_subtasks)
    if not subtasks:
        return {"subtasks": [], "results": [], "answer": ask(client, task)}
    results = []
    for subtask in subtasks:
        results.append(ask(client, f"Task: {task}\nSubtask: {subtask}\nDo only this subtask."))
    numbered = "\n".join(f"{i}. {result}" for i, result in enumerate(results, start=1))
    answer = ask(
        client,
        f"Combine these results into one answer for the task.\n\nTask: {task}\n\nResults:\n{numbered}",
    )
    return {"subtasks": subtasks, "results": results, "answer": answer}

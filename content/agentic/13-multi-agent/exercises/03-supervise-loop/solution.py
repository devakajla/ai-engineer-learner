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


def run_worker(client, name, worker, task, context=""):
    prompt = task if not context else f"{task}\n\nWork so far:\n{context}"
    return {"worker": name, "output": ask(client, prompt, system=worker["system"])}


def format_results(results):
    return "\n".join(f"{r['worker']}: {r['output']}" for r in results)


def supervisor_prompt(task, workers, results):
    lines = "\n".join(f"- {name}: {w['description']}" for name, w in workers.items())
    done = format_results(results) if results else "(nothing yet)"
    return (
        f"Task: {task}\n\nWorkers:\n{lines}\n\nWork so far:\n{done}\n\n"
        "Which worker should act next? Reply with one worker name, or FINISH if the task is done."
    )


def parse_choice(reply, names):
    text = reply.strip().strip(".!\"' `")
    for name in names:
        if text.lower() == name.lower():
            return name
    if text.upper() == "FINISH":
        return "FINISH"
    return None


# Your task:
def supervise(client, workers, task, max_steps=4):
    results = []
    finished = False
    for _ in range(max_steps):
        reply = ask(client, supervisor_prompt(task, workers, results))
        choice = parse_choice(reply, list(workers))
        if choice == "FINISH":
            finished = True
            break
        if choice is None:
            break  # an unknown worker name: stop, do not guess
        results.append(run_worker(client, choice, workers[choice], task, format_results(results)))
    return {"results": results, "steps": len(results), "finished": finished}

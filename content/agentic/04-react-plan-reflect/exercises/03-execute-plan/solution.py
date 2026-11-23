# Given from earlier exercises. Do not change these.
def build_step_messages(goal, steps, results, i):
    numbered = "\n".join(f"{n}. {step}" for n, step in enumerate(steps, start=1))
    done = results[:i]
    if done:
        so_far = "\n".join(f"{n}. {result}" for n, result in enumerate(done, start=1))
    else:
        so_far = "(none yet)"
    system = "You are carrying out one step of a plan. Do only the current step."
    user = (
        f"Goal: {goal}\n\nPlan:\n{numbered}\n\nResults so far:\n{so_far}\n\n"
        f"Current step ({i + 1} of {len(steps)}): {steps[i]}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def execute_plan(client, goal, steps, max_steps=8):
    results = []
    to_run = steps[:max_steps]
    for i in range(len(to_run)):
        messages = build_step_messages(goal, steps, results, i)
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b", messages=messages, temperature=0
        )
        results.append(response.choices[0].message.content.strip())
    return {"results": results, "steps_run": len(to_run), "skipped": len(steps) - len(to_run)}

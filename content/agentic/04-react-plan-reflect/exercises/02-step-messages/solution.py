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

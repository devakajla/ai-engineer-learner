def is_error(result):
    return str(result).startswith("error")


def detect_failure(trace, max_steps=10):
    found = []
    looped = False
    for step in trace:
        same = 0
        for other in trace:
            if other["tool"] == step["tool"] and other["args"] == step["args"]:
                same += 1
        if same >= 3:
            looped = True
    if looped:
        found.append("loop")
    streak = 0
    worst = 0
    for step in trace:
        if is_error(step["result"]):
            streak += 1
            worst = max(worst, streak)
        else:
            streak = 0
    if worst >= 3:
        found.append("error_streak")
    if len(trace) >= max_steps:
        found.append("max_steps")
    return found

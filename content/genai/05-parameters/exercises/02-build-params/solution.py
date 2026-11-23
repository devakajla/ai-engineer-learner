SETTINGS = {
    "extract": {"temperature": 0, "max_completion_tokens": 200},
    "chat": {"temperature": 0.7, "max_completion_tokens": 500},
    "creative": {"temperature": 1.0, "max_completion_tokens": 800},
}


def build_params(task):
    if task not in SETTINGS:
        raise ValueError(f"unknown task: {task}")
    return dict(SETTINGS[task])

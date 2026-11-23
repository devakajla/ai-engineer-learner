def tool_names(trace):
    return [span["name"] for span in trace if span["kind"] == "tool"]


def trajectory_match(actual, expected, mode="exact"):
    if mode == "exact":
        return actual == expected
    if mode == "in_order":
        remaining = iter(actual)
        return all(name in remaining for name in expected)
    if mode == "any_order":
        return all(name in actual for name in expected)
    raise ValueError(f"unknown mode: {mode}")


def step_efficiency(actual, expected):
    if not actual:
        return 1.0 if not expected else 0.0
    return round(min(1.0, len(expected) / len(actual)), 2)

def choose_approach(steps_known, needs_tools, high_risk=False):
    if not needs_tools:
        return "single_call"
    if steps_known:
        return "workflow"
    if high_risk:
        return "agent_with_approval"
    return "agent"

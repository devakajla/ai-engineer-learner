def input_per_step(base_tokens, additions):
    per_step = []
    history = base_tokens
    for added in additions:
        per_step.append(history)
        history += added
    return per_step


def agent_input_cost(base_tokens, additions, input_price):
    total_tokens = sum(input_per_step(base_tokens, additions))
    return round(total_tokens / 1_000_000 * input_price, 6)

def fits(prompt_tokens, max_output, context_limit):
    return prompt_tokens + max_output <= context_limit


def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return round(input_cost + output_cost, 6)


def cheapest_that_fits(models, input_tokens, max_output):
    best_name = None
    best_cost = None
    for name, info in models.items():
        if not fits(input_tokens, max_output, info["context"]):
            continue
        cost = estimate_cost(input_tokens, max_output, info["input_price"], info["output_price"])
        if best_cost is None or cost < best_cost:
            best_name = name
            best_cost = cost
    return best_name

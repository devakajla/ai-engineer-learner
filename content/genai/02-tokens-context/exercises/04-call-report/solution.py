def estimate_tokens(text):
    return (len(text) + 3) // 4


def fits(prompt_tokens, max_output, context_limit):
    return prompt_tokens + max_output <= context_limit


def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return round(input_cost + output_cost, 6)


def call_report(prompt, max_output, context_limit, input_price, output_price):
    tokens = estimate_tokens(prompt)
    ok = fits(tokens, max_output, context_limit)
    cost = 0.0
    if ok:
        cost = estimate_cost(tokens, max_output, input_price, output_price)
    return {"input_tokens": tokens, "fits": ok, "max_cost": cost}

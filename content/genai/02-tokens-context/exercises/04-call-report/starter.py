# Given from the earlier exercises. Do not change them.
def estimate_tokens(text):
    return (len(text) + 3) // 4


def fits(prompt_tokens, max_output, context_limit):
    return prompt_tokens + max_output <= context_limit


def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return round(input_cost + output_cost, 6)


# Your task:
def call_report(prompt, max_output, context_limit, input_price, output_price):
    ...

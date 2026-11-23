def usage_report(usages, input_price, output_price):
    input_tokens = 0
    output_tokens = 0
    for usage in usages:
        input_tokens += usage["prompt_tokens"]
        output_tokens += usage["completion_tokens"]
    cost = input_tokens / 1_000_000 * input_price + output_tokens / 1_000_000 * output_price
    return {
        "calls": len(usages),
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "cost": round(cost, 6),
    }

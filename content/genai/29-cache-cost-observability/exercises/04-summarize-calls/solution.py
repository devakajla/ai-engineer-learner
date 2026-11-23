import math


# Given from earlier exercises. Do not change these.
def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return round(input_cost + output_cost, 6)


def summarize_calls(calls, prices):
    n = len(calls)
    if n == 0:
        return {"n": 0, "errors": 0, "error_rate": 0.0, "total_cost": 0.0, "avg_ms": 0.0, "p95_ms": 0, "unpriced": 0}
    errors = 0
    total_cost = 0.0
    unpriced = 0
    times = []
    for call in calls:
        times.append(call["ms"])
        if not call["ok"]:
            errors += 1
        if call["model"] in prices:
            input_price, output_price = prices[call["model"]]
            total_cost += estimate_cost(call["input"], call["output"], input_price, output_price)
        else:
            unpriced += 1
    times.sort()
    p95_index = math.ceil(0.95 * n) - 1
    return {
        "n": n,
        "errors": errors,
        "error_rate": round(errors / n, 4),
        "total_cost": round(total_cost, 6),
        "avg_ms": round(sum(times) / n, 1),
        "p95_ms": times[p95_index],
        "unpriced": unpriced,
    }

import math


# Given from earlier exercises. Do not change these.
def estimate_cost(input_tokens, output_tokens, input_price, output_price):
    input_cost = input_tokens / 1_000_000 * input_price
    output_cost = output_tokens / 1_000_000 * output_price
    return round(input_cost + output_cost, 6)


# Your task:
def summarize_calls(calls, prices):
    ...

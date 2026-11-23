def request_cost(input_tokens, output_tokens, price_in, price_out):
    return (input_tokens * price_in + output_tokens * price_out) / 1_000_000


def monthly_cost(requests_per_day, input_tokens, output_tokens, price_in, price_out, days=30):
    return round(requests_per_day * days * request_cost(input_tokens, output_tokens, price_in, price_out), 2)

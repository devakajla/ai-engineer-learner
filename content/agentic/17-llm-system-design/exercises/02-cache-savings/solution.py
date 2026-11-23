def cost_with_cache(requests, hit_rate, cost_per_request, cache_cost=0.0):
    if not 0 <= hit_rate <= 1:
        raise ValueError("hit_rate must be between 0 and 1")
    misses = requests * (1 - hit_rate)
    return round(misses * cost_per_request + requests * cache_cost, 2)


def prompt_cache_cost(prefix_tokens, new_tokens, output_tokens, price_in, price_out, cached_price_in, cache_hit):
    prefix_price = cached_price_in if cache_hit else price_in
    return (prefix_tokens * prefix_price + new_tokens * price_in + output_tokens * price_out) / 1_000_000


def savings_percent(before, after):
    if before == 0:
        return 0.0
    return round(100 * (before - after) / before, 1)

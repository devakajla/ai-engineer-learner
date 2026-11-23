# What does caching save?

Two caches cut cost and time (GenAI lesson 29):

- **Response cache:** the same (or a very similar) question gets a stored answer, with **no model call**. The share of questions served from the cache is the **hit rate**. A lookup is not free, but it is cheap.
- **Prompt (prefix) cache:** providers charge **less** for input tokens they have seen recently at the start of the prompt (the system prompt, the tool list, a long document). Put the stable text first, and the part that changes last.

Write:

1. `cost_with_cache(requests, hit_rate, cost_per_request, cache_cost=0.0)`: only the misses call the model. `requests * (1 - hit_rate) * cost_per_request + requests * cache_cost`, rounded to 2 decimals. If `hit_rate` is not between 0 and 1 (both allowed), raise `ValueError("hit_rate must be between 0 and 1")`.
2. `prompt_cache_cost(prefix_tokens, new_tokens, output_tokens, price_in, price_out, cached_price_in, cache_hit)`: the cost of one request (prices per million tokens). The prefix costs `cached_price_in` per million when `cache_hit` is true, otherwise `price_in`. The new tokens cost `price_in`, the output costs `price_out`. Divide the total by `1_000_000`.
3. `savings_percent(before, after)`: `100 * (before - after) / before`, rounded to 1 decimal. If `before` is `0`, return `0.0`.

```python
cost_with_cache(1000, 0.3, 0.01, 0.0001)
# -> 7.1
prompt_cache_cost(4000, 200, 300, 1.0, 4.0, 0.1, True)
# -> 0.0018
```

(Discount sizes and rules differ by provider and change: check the docs.)

**Think first:** a cache with a 30% hit rate saves about 29% in the first example, not 30%. Why?

**Hint:** the same three lines of arithmetic in each function. No loops.

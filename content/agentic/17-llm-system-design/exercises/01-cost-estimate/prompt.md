# What will this cost per month?

Every design interview and every real project needs this back-of-the-envelope number. Model prices are quoted **in dollars per million tokens**, one price for input tokens and one for output tokens (output is usually more expensive). You met this in GenAI lesson 2.

Write:

1. `request_cost(input_tokens, output_tokens, price_in, price_out)`: the dollar cost of one request. `(input_tokens * price_in + output_tokens * price_out) / 1_000_000`.
2. `monthly_cost(requests_per_day, input_tokens, output_tokens, price_in, price_out, days=30)`: `requests_per_day * days * request_cost(...)`, rounded to 2 decimals.

```python
request_cost(1000, 500, 0.5, 1.5)
# -> 0.00125
monthly_cost(1000, 2000, 500, 0.5, 1.5)
# -> 52.5
```

(The prices here are made up. Real prices change: check your provider's page.)

**Think first:** an agent makes 6 model calls per question, and each call re-sends the growing history. Why is the real cost more than "6 times one call"?

**Hint:** use the first function inside the second.

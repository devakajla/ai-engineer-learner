# Estimate the cost of a call

Prices are given **per 1 million tokens**, and input and output have different prices.

Write `estimate_cost(input_tokens, output_tokens, input_price, output_price)`. Return the total cost of one call, rounded to 6 decimal places.

Rules:
- Input cost is `input_tokens / 1_000_000 * input_price`.
- Output cost is `output_tokens / 1_000_000 * output_price`.
- Return the two costs added together, rounded with `round(value, 6)`.

```python
estimate_cost(1_000_000, 1_000_000, 0.5, 1.5)   # -> 2.0
estimate_cost(1000, 500, 0.05, 0.08)            # -> 9e-05
estimate_cost(0, 0, 0.5, 1.5)                   # -> 0.0
```

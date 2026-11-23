# A cost table for all models

You have a few models. Each one has an input price and an output price (per 1 million tokens). Show the cost of the same call on each one.

Your `estimate_cost` function from lesson 2 is **given** in `starter.py`. Do not change it.

Write `cost_table(models, input_tokens, output_tokens)`. `models` is a dictionary `{name: {"input_price": ..., "output_price": ...}}`. Return a dictionary `{name: cost}`, with the cost from `estimate_cost`.

Rules:
- Keep the same order as `models`.
- An empty `models` gives `{}`.

**Think first:** What do you loop over, and what do you put in the new dictionary?

**Hint:** One call to `estimate_cost` for each model.

```python
models = {
    "small": {"input_price": 0.05, "output_price": 0.08},
    "big": {"input_price": 0.6, "output_price": 0.8},
}

cost_table(models, 1000, 500)
# -> {'small': 9e-05, 'big': 0.001}
```

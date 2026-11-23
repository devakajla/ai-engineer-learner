# Cheapest model that fits

Pick the cheapest model whose context window can hold your call.

Your `estimate_cost` (lesson 2) and `fits` (lesson 2) functions are **given** in `starter.py`. Do not change them.

Write `cheapest_that_fits(models, input_tokens, max_output)`. `models` is a dictionary `{name: {"input_price": ..., "output_price": ..., "context": ...}}`.

Rules:
- Skip a model if the call does not fit its `"context"` (use `fits`).
- The cost of a model is `estimate_cost(input_tokens, max_output, input_price, output_price)`.
- Return the **name** of the cheapest model that fits.
- If two models cost the same, return the one that comes first.
- If no model fits, return `None`.

**Think first:** Which models do you skip, and what do you remember while you loop?

**Hint:** The "filter, then find the best" pattern from the lesson (phone plans).

```python
models = {
    "small": {"input_price": 0.05, "output_price": 0.08, "context": 8000},
    "big": {"input_price": 0.6, "output_price": 0.8, "context": 128000},
}

cheapest_that_fits(models, 1000, 500)     # -> 'small'
cheapest_that_fits(models, 20000, 500)    # -> 'big'    (small is too short)
cheapest_that_fits(models, 999999, 500)   # -> None
```

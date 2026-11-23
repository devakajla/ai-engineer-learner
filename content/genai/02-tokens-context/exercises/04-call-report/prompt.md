# Plan a call before you make it

Before you send a prompt, a careful engineer checks the size, the fit and the cost. Put your three earlier helpers together.

The helpers `estimate_tokens`, `fits` and `estimate_cost` are **given** in `starter.py`. Do not change them.

Write `call_report(prompt, max_output, context_limit, input_price, output_price)`. Return a dictionary with these keys:

- `"input_tokens"`: `estimate_tokens(prompt)`.
- `"fits"`: whether the input and `max_output` fit in `context_limit`.
- `"max_cost"`: the cost if the model writes the **full** `max_output` tokens. Use `estimate_cost`.

Rules:
- If the call does not fit, `"max_cost"` must be `0.0`, because you would not send it.

**Think first:** Which of the three answers does the cost depend on?

**Hint:** Work out the tokens first, then check the fit, then decide the cost.

```python
call_report("a" * 400, 100, 4096, 0.5, 1.5)
# -> {'input_tokens': 100, 'fits': True, 'max_cost': 0.0002}

call_report("a" * 400, 4000, 4096, 0.5, 1.5)
# -> {'input_tokens': 100, 'fits': False, 'max_cost': 0.0}
```

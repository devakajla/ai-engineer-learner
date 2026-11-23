# Usage, cost and cut-off from one response

The helpers `usage_summary` and `estimate_cost` (and more) are **given** in `starter.py`. Do not change them.

Write `call_cost(response, input_price, output_price)`. Prices are per 1 million tokens. Return a dictionary with:

- `"usage"`: the dictionary from `usage_summary(response)`.
- `"cost"`: `estimate_cost(input tokens, output tokens, input_price, output_price)`.
- `"cut_off"`: `True` if `response.choices[0].finish_reason == "length"`, otherwise `False`.

**Think first:** Which given helper gives you the token numbers that `estimate_cost` needs?

**Hint:** Call `usage_summary` first and keep its result.

```python
call_cost(response, 0.5, 1.5)
# response used 1000 input and 500 output tokens, finish_reason "stop"
# -> {'usage': {'input': 1000, 'output': 500, 'total': 1500}, 'cost': 0.00125, 'cut_off': False}
```

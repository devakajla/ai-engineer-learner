# Usage and cost report

Every API response has `usage` with token counts. Write `usage_report(usages, input_price, output_price)`. It adds up many calls and works out the cost.

`usages` is a list of dictionaries like `{"prompt_tokens": 1000, "completion_tokens": 200}`. Prices are per **1 million** tokens.

Return a dictionary with these keys:
- `"calls"`: how many items are in `usages`.
- `"input_tokens"`: the sum of `prompt_tokens`.
- `"output_tokens"`: the sum of `completion_tokens`.
- `"cost"`: `input_tokens / 1_000_000 * input_price + output_tokens / 1_000_000 * output_price`, rounded to 6 decimal places.

```python
usage_report(
    [{"prompt_tokens": 1000, "completion_tokens": 200},
     {"prompt_tokens": 3000, "completion_tokens": 800}],
    0.5, 1.5,
)
# -> {'calls': 2, 'input_tokens': 4000, 'output_tokens': 1000, 'cost': 0.0035}

usage_report([], 0.5, 1.5)
# -> {'calls': 0, 'input_tokens': 0, 'output_tokens': 0, 'cost': 0.0}
```

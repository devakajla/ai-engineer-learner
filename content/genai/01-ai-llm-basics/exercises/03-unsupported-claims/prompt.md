# Spot unsupported claims

An LLM can hallucinate, so check its claims against facts you trust.

Write `unsupported(claims, trusted)`. `claims` is a list of strings from the model. `trusted` is a set (or list) of facts you trust.

Return a list of the claims that are **not** in `trusted`. Keep the original order.

```python
trusted = {"Paris is in France", "2 + 2 = 4"}

unsupported(["Paris is in France", "Paris is in Spain"], trusted)
# -> ['Paris is in Spain']

unsupported(["2 + 2 = 4"], trusted)
# -> []
```

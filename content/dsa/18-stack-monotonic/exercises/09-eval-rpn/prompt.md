# Evaluate reverse Polish notation

`tokens` is a list of strings: numbers (can be negative) and the operators `+ - * /`. The operator comes **after** its two numbers. Write `eval_rpn(tokens)` that returns the result as an integer. Division **truncates toward zero** (`7 / -2` is `-3`). The input is always valid.

```python
eval_rpn(["2", "1", "+", "3", "*"])          # -> 9    ((2 + 1) * 3)
eval_rpn(["4", "13", "5", "/", "+"])         # -> 6    (4 + 13 / 5)
```

**Think first:** when you read an operator, which two numbers does it use? Which one is the left side?

**Hint:** pattern *stack*: push numbers; on an operator pop `b` then `a`, push `a op b`. Use `int(a / b)` for division.

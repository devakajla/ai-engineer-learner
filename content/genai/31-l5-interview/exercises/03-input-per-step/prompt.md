# Why long agents are expensive

Every step of an agent sends the **whole history** again. Write two functions.

**`input_per_step(base_tokens, additions)`**
- `base_tokens`: tokens of the system message and the question (the history before step 1).
- `additions`: a list. Item `i` is how many tokens step `i` **adds** to the history (the assistant message plus the tool results).
- Return a list with the **input tokens of each step**. Step 1 sends `base_tokens`. Step 2 sends `base_tokens + additions[0]`, and so on. The length of the result equals the length of `additions`.

**`agent_input_cost(base_tokens, additions, input_price)`**
- The total input cost of all the steps. `input_price` is per million tokens. Return `round(total_tokens / 1_000_000 * input_price, 6)`, where `total_tokens` is the sum of `input_per_step`.

```python
input_per_step(100, [50, 50, 50])          # -> [100, 150, 200]
sum(input_per_step(100, [50, 50, 50]))     # -> 450
agent_input_cost(100, [50, 50, 50], 1.0)   # -> 0.00045
input_per_step(100, [])                    # -> []
```

**Think first:** with 10 steps that add 500 tokens each, is the total about 10 times one step, or much more? What would you do about it?

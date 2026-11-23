# Write two tools

In LangChain a **tool** is a Python function with the `@tool` decorator. LangChain reads three things for you:

- the **name** from the function name,
- the **description** from the docstring (this is what the model reads to decide when to use the tool),
- the **arguments** from the type hints.

Write two tools and a function that returns them:

1. `convert_temp(celsius: float) -> float`: convert Celsius to Fahrenheit (`celsius * 9 / 5 + 32`). Docstring: `"""Convert a temperature from Celsius to Fahrenheit."""`
2. `word_count(text: str) -> int`: count the words (split on white space). Docstring: `"""Count the words in a text."""`
3. `make_tools()`: return the list `[convert_temp, word_count]`.

```python
convert_temp.invoke({"celsius": 100})
# -> 212.0
word_count.invoke({"text": "one two three"})
# -> 3
```

**Think first:** the model never sees your code. What does it see?

**Hint:** put `@tool` on the line above `def`. Keep the docstring exactly as given, the test checks it.

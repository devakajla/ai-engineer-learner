# Add your own step to a chain

Any normal Python function can become a step in a chain. Wrap it with `RunnableLambda(function)` and join it with `|`.

Models often add quotes or an explanation. Write two things:

1. `clean_title(text)`: keep only the **first line** of `text`, remove spaces at both ends, then remove quote characters (`"` and `'`) at both ends, and remove spaces again.
2. `build_title_chain(model)`: a prompt with two messages, a **system** message `"Write a short title for the text. Reply with the title only."` and a **human** message `"{text}"`. Then `| model | StrOutputParser() | RunnableLambda(clean_title)`.

The imports and `build_chain` from exercise 1 are given.

```python
clean_title('  "Rain in Pune"  ')
# -> 'Rain in Pune'
clean_title('"A title"\nHere is why.')
# -> 'A title'
```

**Think first:** why clean the model's answer in the chain, and not in the code that calls the chain?

**Hint:** `text.strip().split("\n")[0]` gives the first line. `.strip("\"'")` removes quotes from both ends.

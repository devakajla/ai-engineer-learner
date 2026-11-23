# A chain that returns a dict

A parser can do more than turn a message into text. `JsonOutputParser()` reads JSON text from the model and returns a Python dict. It also copes with a reply wrapped in a markdown code fence.

The imports and `build_chain` are given. Write `build_json_chain(model)`:

1. A prompt with a **system** message: `'Read the sentence and reply with JSON only, in this shape: {{"name": "<person name>", "age": <number>}}'` and a **human** message `"{sentence}"`.
2. Return `prompt | model | JsonOutputParser()`.

Look at the **double braces** `{{ }}` in the system message. In a prompt template `{name}` means "fill in a variable". To write a real brace you must double it. The prompt then shows `{"name": ..., "age": ...}`.

```python
chain.invoke({"sentence": "Asha is 21 years old."})
# -> {'name': 'Asha', 'age': 21}
```

**Think first:** what happens if you forget the double braces?

**Hint:** copy the system message text exactly. Only `{sentence}` is a variable.

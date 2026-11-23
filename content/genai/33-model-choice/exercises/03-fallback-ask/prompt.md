# Ask with a fallback model

Write `ask_with_fallback(client, model_names, messages)`. It tries the models in order and returns the first answer that works.

Rules:
- Call `client.chat.completions.create(model=name, messages=messages)` for each name, in order.
- On success, return a tuple `(name, text)`. The text is `response.choices[0].message.content`.
- If a call raises any exception, remember it and try the next model.
- If every model fails, raise the **last** exception.
- If `model_names` is empty, raise `ValueError("no models to try")`.
- Do not wait between tries. Tests must stay fast.

**Think first:** What do you do when a call fails, and what must you keep until the end?

**Hint:** The `first_that_works` pattern from the lesson, with a loop over model names.

```python
ask_with_fallback(client, ["big", "small"], messages)
# big fails, small works -> ('small', 'the answer')

ask_with_fallback(client, ["big"], messages)
# big works -> ('big', 'the answer')
```

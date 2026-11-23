# Ask the model

Write `ask(client, question, model="qwen/qwen3.8-27b")`. It sends one user message to the model and returns the text of the answer.

Rules:
- Call `client.chat.completions.create(model=model, messages=messages)`.
- `messages` is a list with one dictionary: role `"user"`, content is the `question`.
- Return `response.choices[0].message.content`.

In the tests, `client` is a fake. It works like the real one but needs no internet.

```python
ask(client, "What is 2+2?")
# -> 'It is 4.'   (whatever text the model returns)

ask(client, "Hi", model="llama-3.3-70b-versatile")
# sends model="llama-3.3-70b-versatile"
```

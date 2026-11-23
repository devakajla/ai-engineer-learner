# The Level 2 assistant

Put everything together. Write `assistant(client, registry, name, values, question, examples=None, tools=None, functions=None, model_class=None)`. It is one function that can answer in three ways.

In the starter you have everything from before: `prepare_messages` (exercise 1), `ask_structured` (exercise 2), and `chat_with_tools` (lesson 11).

Rules:
1. If both `tools` and `model_class` are given, raise `ValueError("use tools or model_class, not both")` **before** any call.
2. Build the messages with `prepare_messages(registry, name, values, question, examples)`.
3. If `model_class` is given: return `ask_structured(client, messages, model_class)`.
4. Else if `tools` is given: return `chat_with_tools(client, messages, tools, functions or {})`.
5. Else make one plain call: `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, temperature=0)` and return `response.choices[0].message.content`.

```python
assistant(client, registry, "tutor", {"level": "kind"}, "What is a list?")
# -> 'A list holds items in order.'   (plain text)

assistant(client, registry, "ticketer", {}, "Login crashes", model_class=Ticket)
# -> Ticket(title='Login crash', priority=5, tags=[])

assistant(client, registry, "helper", {}, "What is 2+3?", tools=tools, functions={"add": add})
# -> 'It is 5.'
```

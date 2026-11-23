# Prepare the messages

Write `prepare_messages(registry, name, values, question, examples=None, version=None)`. It builds the full `messages` list for one call. It joins three ideas from Level 2: a stored prompt template (lesson 8), few-shot examples (lesson 7) and the user's question.

`render_prompt` and `examples_to_messages` are already in the starter. Use them.

Rules:
1. The first message is the `system` message. Its content is the stored prompt `name` (version `version`, or the newest when `None`), filled with `values`.
2. Then come the example messages (from `examples`, a list of `(input, output)` pairs). `examples` can be `None`: add nothing.
3. The last message is the `user` message with `question`.
4. A missing placeholder value raises `ValueError` (this comes from `render_prompt`, do not catch it).

```python
registry = {"tutor": {"v1": "You are a {level} tutor."}}
prepare_messages(registry, "tutor", {"level": "kind"}, "What is a list?")
# -> [{'role': 'system', 'content': 'You are a kind tutor.'},
#     {'role': 'user', 'content': 'What is a list?'}]

prepare_messages(registry, "tutor", {"level": "kind"}, "3+3?", examples=[("2+2", "4")])
# -> [system, {'role': 'user', 'content': '2+2'}, {'role': 'assistant', 'content': '4'},
#     {'role': 'user', 'content': '3+3?'}]
```

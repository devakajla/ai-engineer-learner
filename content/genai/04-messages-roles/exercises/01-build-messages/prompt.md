# Build the messages list

Write `build_messages(system, user)`. It returns the list of messages to send to the model.

Rules:
- The first message has role `"system"` and content `system`.
- The second message has role `"user"` and content `user`.
- If `system` is an empty string or `None`, leave the system message out. Return only the user message.

```python
build_messages("Be brief.", "Hi")
# -> [{'role': 'system', 'content': 'Be brief.'}, {'role': 'user', 'content': 'Hi'}]

build_messages("", "Hi")
# -> [{'role': 'user', 'content': 'Hi'}]
```

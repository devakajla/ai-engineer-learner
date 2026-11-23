# Ask for any shape, with repair

In lesson 10 you wrote a repair loop for one model (`Ticket`). Now make it work for **any** Pydantic model.

Write `ask_structured(client, messages, model_class, max_tries=3)`. The helper `check_reply(model_class, text)` is in the starter. It returns `(result, None)` when the reply is valid, and `(None, error_text)` when it is not.

Rules:
- Each call is `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, response_format={"type": "json_object"}, temperature=0)`.
- Take the reply text from `response.choices[0].message.content` and check it with `check_reply`. If valid, return the result.
- If not valid, make a **new** list: the messages, plus an `assistant` message with the bad reply, plus a `user` message `f"Your reply was invalid: {error}\nFix it and reply with JSON only."`. Call again with the new list.
- Make at most `max_tries` calls. After that, raise `ValueError("could not get a valid reply")`.
- Do not change the `messages` list that was passed in.

```python
ask_structured(client, messages, Ticket)
# 1st reply: '{"title": "x", "priority": 9}'  (invalid)
# 2nd call sends the bad reply and the error
# 2nd reply: '{"title": "x", "priority": 4}'
# -> Ticket(title='x', priority=4, tags=[])
```

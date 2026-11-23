# Ask for a ticket, with repair

The `Ticket` model is written for you. Write `ask_ticket(client, text, max_tries=3)`. It asks the model to turn `text` into a ticket. If the reply is invalid, it sends the error back and tries again.

Rules:
- Start with these messages:
  1. `system`: `"Reply with JSON only. Keys: title (string), priority (integer 1 to 5), tags (list of strings)."`
  2. `user`: the `text`.
- Each call is `client.chat.completions.create(model="qwen/qwen3.8-27b", messages=messages, response_format={"type": "json_object"}, temperature=0)`.
- Check the reply with `Ticket.model_validate_json(reply)`. If it works, return the ticket.
- If it raises `ValidationError`, add two messages to the list (as a **new list**): an `assistant` message with the bad reply, and a `user` message with this text: `f"Your reply was invalid: {error}\nFix it and reply with JSON only."` Then call again.
- Make at most `max_tries` calls. If all replies are invalid, raise `ValueError("could not get a valid ticket")`.

```python
ask_ticket(client, "Login page crashes, very urgent")
# 1st reply: '{"title": "Login crash", "priority": 9}'   (invalid)
# 2nd call sends the bad reply + the error message
# 2nd reply: '{"title": "Login crash", "priority": 5}'
# -> Ticket(title='Login crash', priority=5, tags=[])
```

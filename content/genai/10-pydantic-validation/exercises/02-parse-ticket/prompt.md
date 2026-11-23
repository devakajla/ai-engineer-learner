# Parse a ticket from model JSON

The `Ticket` model is already written for you in the starter. Write `parse_ticket(text)`.

Rules:
- Turn the JSON `text` into a `Ticket`. Use `Ticket.model_validate_json(text)`.
- If the text is not valid JSON, or the fields are wrong, return `None`. Do not raise.

```python
parse_ticket('{"title": "Login broken", "priority": 2}')
# -> Ticket(title='Login broken', priority=2, tags=[])

parse_ticket('{"title": "x", "priority": 9}')    # -> None  (priority too big)
parse_ticket("hello")                            # -> None  (not JSON)
parse_ticket('{"priority": 2}')                  # -> None  (title is missing)
```

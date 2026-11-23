# The Ticket model

Write a Pydantic model `Ticket` for a support ticket.

Fields:
- `title`: a string, at least 1 character.
- `priority`: an integer from `1` to `5` (including 1 and 5).
- `tags`: a list of strings. It is optional and its default is an empty list.

Pydantic gives you the checks for free, so there is no extra code to write.

```python
Ticket(title="Login broken", priority=3)
# -> Ticket(title='Login broken', priority=3, tags=[])

Ticket(title="Slow", priority="2", tags=["perf"]).priority
# -> 2        (the string "2" is converted)

Ticket(title="", priority=3)     # raises ValidationError (empty title)
Ticket(title="x", priority=6)    # raises ValidationError (above 5)
```

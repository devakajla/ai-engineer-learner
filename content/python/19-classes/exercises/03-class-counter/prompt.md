# Count instances, keep state separate

Write a class `Ticket`:

- each ticket gets a unique, increasing `id` starting at **1** (use a class attribute counter)
- `Ticket(title)` stores `title` and a **per-instance** list `comments` (starts empty)
- `add_comment(text)` appends to that ticket's comments only
- `Ticket.total_created()` — a classmethod returning how many tickets were created
- `Ticket.reset_counter()` — a classmethod that sets the counter back to 0 (the tests use it)

```python
Ticket.reset_counter()
a = Ticket("Login bug"); b = Ticket("Slow page")
a.id, b.id               # -> (1, 2)
a.add_comment("repro?")
b.comments               # -> []
Ticket.total_created()   # -> 2
```

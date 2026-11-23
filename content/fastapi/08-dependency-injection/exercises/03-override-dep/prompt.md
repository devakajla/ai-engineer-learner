# Inject a notifier, fake it in tests

The app sends a notification when a comment is created. Write:

- `class EmailNotifier` with `send(to: str, message: str) -> None` (it just appends to its own `sent` list — pretend it's SMTP)
- a dependency `get_notifier()` that returns a **single shared** `EmailNotifier` instance
- `POST /comments` with body `{"author": str, "text": str}` → 201 and `{"id": <n>, "author": ..., "text": ...}`; it calls `notifier.send(author, "Thanks for your comment")` using the **injected** notifier

The tests will replace the notifier with a fake through `app.dependency_overrides[get_notifier]` and check what was sent.

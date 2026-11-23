# ORM model + CRUD

With SQLAlchemy 2.0 (no FastAPI yet), write:

- `class Base(DeclarativeBase)`
- model `Book` → table `books`: `id` (PK), `title` (`String(200)`, required), `author` (`String(100)`, required), `year` (int, **nullable**), `available` (bool, default `True`, **indexed**)
- functions taking a `Session`:
  - `add_book(session, title, author, year=None) -> Book` (commit + refresh, return it)
  - `available_by(session, author) -> list[Book]` — available books by that author, ordered by `year` then `title`, using `select()`
  - `checkout(session, book_id) -> bool` — set `available=False`; `False` if missing or already checked out
  - `count_available(session) -> int` — using `func.count()`

The tests create an in-memory engine and call `Base.metadata.create_all(engine)` themselves.

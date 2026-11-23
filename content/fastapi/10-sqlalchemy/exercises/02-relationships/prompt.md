# Relationships without N+1

Write models (with your own `Base`):

- `Author` → `authors`: `id`, `name` (`String(100)`), `books: Mapped[list["Book"]] = relationship(back_populates="author")`
- `Book` → `books`: `id`, `title` (`String(200)`), `author_id` (FK to `authors.id`), `author` relationship back to `Author`

And `book_counts(session) -> list[tuple[str, int]]`: each author's name and number of books, ordered by name. **It must run at most 2 SQL queries** no matter how many authors there are — load the authors with `selectinload(Author.books)` and count in Python, **or** do a single `GROUP BY` query.

The tests count the SQL statements executed.

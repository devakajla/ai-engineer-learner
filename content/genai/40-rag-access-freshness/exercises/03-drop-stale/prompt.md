# Drop old chunks

Old documents can give wrong answers (an old price, an old API version). Remove hits that are too old.

Write `drop_stale(hits, today, max_age_days)`.

- Each hit may have `"updated"`: a date text like `"2026-03-15"`.
- `today` is a date text like `"2026-11-23"`.
- The age in days is `today - updated`.

Rules:
- Keep a hit if its age is `<= max_age_days`.
- A hit with **no** `"updated"` key is kept (we do not know its age).
- A date in the future has a negative age, so it is kept.
- Keep the order.

Hint: `from datetime import date` is in the starter. `date.fromisoformat("2026-03-15")` makes a date. Subtracting two dates gives a `timedelta`; its `.days` is a number.

```python
hits = [{"id": "a", "updated": "2026-11-01"}, {"id": "b", "updated": "2025-01-01"}, {"id": "c"}]
drop_stale(hits, "2026-11-23", 365)    # -> [{'id': 'a', ...}, {'id': 'c'}]
```

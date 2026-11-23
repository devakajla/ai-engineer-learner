# Time-zone-safe deadlines

Write (all datetimes **aware**):

- `parse_due(text)` → parse an ISO 8601 string **with an offset** (e.g. `"2026-11-20T18:00:00+05:30"`) and return it converted to **UTC**. If the string has no offset (naive), raise `ValueError("timezone required")`.
- `is_overdue(due, now)` → `True` if `now` is after `due` (both aware).
- `time_left(due, now)` → a human string: `"overdue"` if past, else `"<d>d <h>h"` (whole days and remaining whole hours), e.g. `"2d 5h"`.
- `display(dt, tz_name)` → format in the given zone as `"20 Nov 2026, 06:00 PM"` (`%d %b %Y, %I:%M %p`) using `zoneinfo`.

```python
due = parse_due("2026-11-20T18:00:00+05:30")
due.isoformat()                     # -> "2026-11-20T12:30:00+00:00"
display(due, "Asia/Kolkata")        # -> "20 Nov 2026, 06:00 PM"
```

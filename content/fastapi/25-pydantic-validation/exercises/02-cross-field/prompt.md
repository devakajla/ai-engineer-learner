# A booking with dates that must make sense

Create `app` with `POST /bookings`.

The body model `BookingIn`:

| Field | Type | Rules |
|---|---|---|
| `guest` | str | 1-50 characters |
| `check_in` | date | |
| `check_out` | date | must be **after** `check_in` |
| `rooms` | int | 1-5, default 1 |

The "after" rule involves **two fields**, so use a `model_validator(mode="after")`.

The answer is **201** with a response model `BookingOut` that has the same fields **plus** a computed field `nights` (the number of days between `check_in` and `check_out`):

```text
POST /bookings {"guest": "Ana", "check_in": "2026-03-01", "check_out": "2026-03-04"}
-> 201 {"guest": "Ana", "check_in": "2026-03-01", "check_out": "2026-03-04", "rooms": 1, "nights": 3}

POST /bookings {"guest": "Ana", "check_in": "2026-03-04", "check_out": "2026-03-04"}  -> 422
```

**Think first:** Why can this rule not be a `field_validator` on a single field?

**Hint:** `from datetime import date`. Subtracting two dates gives a `timedelta`, and `.days` is its number of days. `@computed_field` goes on a `@property`.

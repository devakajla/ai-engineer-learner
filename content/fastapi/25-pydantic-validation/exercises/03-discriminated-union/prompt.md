# One endpoint, three kinds of message

Create `app` with `POST /notify`. The body can be one of **three shapes**. The field `channel` tells which one:

| `channel` | other fields |
|---|---|
| `"email"` | `to` (str, must contain `@`), `subject` (str, 1-100 characters) |
| `"sms"` | `phone` (str, exactly 10 digits) |
| `"push"` | `device_id` (str, at least 1 character) |

Make one model for each shape. Use `Literal` for `channel`. Take the three models as a **discriminated union**, so FastAPI picks the right model from `channel` and reports errors for that model only.

The answer is **200** with `{"sent_via": <channel>, "target": <to, phone or device_id>}`:

```text
POST /notify {"channel": "email", "to": "a@x.io", "subject": "Hi"}  -> {"sent_via": "email", "target": "a@x.io"}
POST /notify {"channel": "sms", "phone": "9876543210"}              -> {"sent_via": "sms", "target": "9876543210"}
POST /notify {"channel": "fax", "phone": "9876543210"}              -> 422
```

**Think first:** How does Pydantic know which of the three models to use for a body?

**Hint:** `Annotated[Email | Sms | Push, Field(discriminator="channel")]` as the type of the route parameter. Use `isinstance(...)` or `match` to read the right field.

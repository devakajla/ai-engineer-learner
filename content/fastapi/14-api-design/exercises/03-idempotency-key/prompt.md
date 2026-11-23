# Idempotency keys for safe retries

`POST /payments` with body `{"amount": int > 0, "currency": str}` creates a payment `{"id", "amount", "currency"}` and returns **201**. Clients may send an `Idempotency-Key` header:

- **No key** → always create a new payment.
- **New key** → create the payment, remember `(key → request body, status, response)` in `IDEMPOTENCY_STORE` (a dict).
- **Same key, same body** → do **not** create another payment; return the stored response with the same status code and the header `Idempotent-Replayed: true`.
- **Same key, different body** → **422** `{"detail": "Idempotency-Key reused with a different request"}`.

`PAYMENTS` (a list) must only grow when a payment is really created.

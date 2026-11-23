# Interview task: don't oversell (25 min)

A flash sale has `STOCK = {"tshirt": 5}`. `POST /reserve/{item}` reserves one unit:

- **200** `{"item": ..., "remaining": n}` when a unit was reserved
- **409** `{"detail": "Sold out"}` when stock is 0
- **404** `{"detail": "Unknown item"}` for unknown items

The starter has a **race condition**: between checking the stock and decrementing it, it awaits a (simulated) payment-hold call, so concurrent requests all see `stock > 0` and the shop oversells.

Fix it so that **20 concurrent requests** produce exactly 5 successes and 15 × 409, and stock never goes negative. Keep the `await hold_payment()` call (it's real I/O). Use an `asyncio.Lock` **per item**.

Discussion for the interview: this lock only works inside **one process**. With several workers/servers you'd use the database (`UPDATE ... SET stock = stock - 1 WHERE item = :i AND stock > 0` and check the affected rows, or `SELECT ... FOR UPDATE`) or a Redis atomic `DECR`.

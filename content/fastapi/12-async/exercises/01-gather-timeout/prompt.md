# Concurrent calls with timeouts

`fetch_price(symbol)` (given) simulates a slow API: it takes 0.2 s, and the symbol `"SLOW"` takes 5 s.

Write:

- `async def fetch_all(symbols, timeout=0.5) -> dict[str, float | None]` — fetch all prices **concurrently**; any call slower than `timeout` gives `None` for that symbol (use `asyncio.wait_for`). Keys in the input order.
- `GET /prices?symbols=AAPL,MSFT` — an **async** route that splits the comma-separated list and returns `fetch_all(...)`.

```text
fetch_all(["A", "B", "C", "D", "E"])   # ~0.2 s total, not 1 s
fetch_all(["A", "SLOW"])               # -> {"A": 1.0, "SLOW": None} in ~0.5 s
```

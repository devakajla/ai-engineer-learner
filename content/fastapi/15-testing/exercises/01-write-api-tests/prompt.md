# Write tests that catch bugs

This time **you write the tests**. The app is in `app_under_test.py` (it's next to your file at run time — import it with `from app_under_test import app`).

**The rules of `POST /quote`:**

- body: `{"items": [{"price": float > 0, "qty": int ≥ 1}, ...] (at least one), "coupon": str | null}`
- `subtotal` = Σ price × qty
- coupon `"SAVE10"` → discount 10% of subtotal; any other coupon → **400** `{"detail": "Invalid coupon"}`
- subtotal **≥ 1000** → extra flat discount of 50
- `total = subtotal - discount`; all three numbers rounded to 2 decimals
- invalid body (no items, price ≤ 0, qty < 1) → 422

Write `test_*` functions in your solution that check these rules with `TestClient`.

**How you're graded:** your tests must **pass** on the correct app, and **fail** on 5 secretly broken versions of it (wrong coupon rate, wrong bulk threshold, unknown coupons accepted, missing rounding, quantity ignored). Use `@pytest.mark.parametrize` where it helps.

Hint: test the *edges* — e.g. a subtotal of exactly 1000, a price like 0.1 × 3.

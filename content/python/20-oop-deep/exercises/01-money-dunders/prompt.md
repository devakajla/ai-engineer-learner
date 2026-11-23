# Money that behaves like a number

Write `Money(amount: int, currency: str = "INR")` (amount in paise/cents) with:

- `__repr__` → `Money(500, 'INR')`
- `__eq__`: equal if amount **and** currency match; comparing with a non-Money returns `NotImplemented` (so `Money(1) == 1` is `False`)
- `__hash__` consistent with `__eq__` (usable in sets and as dict keys)
- `__add__`: same currency → new `Money`; different currency → `ValueError`
- `__lt__` so `sorted()` / `min()` work (same currency only; else `ValueError`)
- `__bool__`: `False` when amount is 0

```python
Money(500) + Money(250)              # -> Money(750, 'INR')
{Money(1), Money(1)}                 # -> {Money(1, 'INR')}
sorted([Money(3), Money(1)])         # -> [Money(1, 'INR'), Money(3, 'INR')]
bool(Money(0))                       # -> False
```

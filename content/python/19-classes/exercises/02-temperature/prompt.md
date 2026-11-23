# Temperature with properties

Write `Temperature`:

- `Temperature(celsius)` — stores the value
- `celsius` property with a **setter** that raises `ValueError` below `-273.15`
- `fahrenheit` property (read **and** write): reading converts from celsius (`c * 9/5 + 32`); setting converts back and goes through the same validation
- `Temperature.from_fahrenheit(f)` — a **classmethod** alternative constructor

```python
t = Temperature(100)
t.fahrenheit            # -> 212.0
t.fahrenheit = 32
t.celsius               # -> 0.0
Temperature.from_fahrenheit(212).celsius   # -> 100.0
Temperature(-300)       # ValueError
```

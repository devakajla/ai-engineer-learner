# Clamp the temperature

Groq accepts temperatures from `0` to `2`. Write `clamp_temperature(t)` to keep any number inside that range.

Rules:
- If `t` is below `0`, return `0.0`.
- If `t` is above `2`, return `2.0`.
- Otherwise return `t` as a float.
- Always return a `float`.

```python
clamp_temperature(0.7)    # -> 0.7
clamp_temperature(-1)     # -> 0.0
clamp_temperature(5)      # -> 2.0
clamp_temperature(1)      # -> 1.0
```

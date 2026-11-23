# Squeeze numbers into one byte

**Quantization** stores each number with fewer bits. The simplest kind is **symmetric int8**: find the biggest absolute value, and spread all numbers over the whole numbers from -127 to 127.

- `scale = biggest_absolute_value / 127`
- `quantized = round(value / scale)` (a small whole number, fits in 1 byte)
- to get the number back: `value ~ quantized * scale`

You lose a little detail (the **rounding error**), and you save memory: 1 byte instead of 2 or 4.

Write:

1. `quantize(values)`: return `(quantized_list, scale)`. If every value is `0` (or the list is empty), use `scale = 1.0` and no division by zero.
2. `dequantize(quantized, scale)`: the list of `q * scale`.
3. `max_error(values)`: quantize, dequantize, and return the biggest `abs(original - restored)` (`0.0` for an empty list).

```python
quantize([12.7, -12.7, 0.0, 3.0])
# -> ([127, -127, 0, 30], 0.1)
```

**Think first:** one huge value (an **outlier**) makes the scale big. What happens to the small values? (The last test shows it.)

**Hint:** `max((abs(v) for v in values), default=0)` works on an empty list too.

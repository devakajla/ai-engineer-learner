# Receipt line

Write `receipt_line(item, qty, price)` that returns one line of a receipt:

- `item` left-aligned in a field 10 characters wide
- then `x` and the quantity
- then ` = ₹` and the total (`qty * price`) with **exactly 2 decimals** and a thousands separator

```python
receipt_line("Coffee", 2, 120.25)   # -> "Coffee     x2 = ₹240.50"
receipt_line("Laptop", 1, 75999)    # -> "Laptop     x1 = ₹75,999.00"
```

Note there is one space between the 10-wide item field and `x`. Use a single f-string.

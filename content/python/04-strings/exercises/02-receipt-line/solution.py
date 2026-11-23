def receipt_line(item, qty, price):
    return f"{item:<10} x{qty} = ₹{qty * price:,.2f}"

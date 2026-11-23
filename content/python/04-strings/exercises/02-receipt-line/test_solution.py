from solution import receipt_line


def test_examples():
    assert receipt_line("Coffee", 2, 120.25) == "Coffee     x2 = ₹240.50"
    assert receipt_line("Laptop", 1, 75999) == "Laptop     x1 = ₹75,999.00"


def test_long_name_is_not_cut():
    assert receipt_line("Headphones", 3, 10) == "Headphones x3 = ₹30.00"


def test_rounding():
    assert receipt_line("Tea", 3, 0.333) == "Tea        x3 = ₹1.00"

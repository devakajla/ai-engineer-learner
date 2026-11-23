from solution import days_between


def test_examples():
    assert days_between("2025-01-01", "2025-03-01") == 59
    assert days_between("2025-03-01", "2025-01-01") == -59


def test_more():
    assert days_between("2025-05-05", "2025-05-05") == 0
    assert days_between("2024-02-28", "2024-03-01") == 2, "2024 is a leap year"
    assert isinstance(days_between("2025-01-01", "2025-01-02"), int)

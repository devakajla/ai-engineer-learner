from solution import days_in_month


def test_examples():
    assert days_in_month(1, 2023) == 31
    assert days_in_month(2, 2024) == 29
    assert days_in_month(2, 2023) == 28
    assert days_in_month(4, 2023) == 30


def test_more():
    assert days_in_month(12, 2023) == 31
    assert days_in_month(2, 1900) == 28
    assert days_in_month(2, 2000) == 29
    assert days_in_month(11, 2024) == 30

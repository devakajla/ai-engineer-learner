from solution import status_report, top_spenders

ORDERS = [
    {"user": "a", "status": "paid", "amount": 10.0},
    {"user": "b", "status": "cancelled", "amount": 500.0},
    {"user": "c", "status": "paid", "amount": 2.5},
    {"user": "b", "status": "refunded", "amount": 1.1},
    {"user": "a", "status": "paid", "amount": 0.2},
    {"user": "c", "status": "paid", "amount": 7.7},
]


def test_report_unsorted_input():
    assert status_report(ORDERS) == [("cancelled", 1, 500.0), ("paid", 4, 20.4), ("refunded", 1, 1.1)]


def test_report_empty():
    assert status_report([]) == []


def test_top_spenders():
    assert top_spenders(ORDERS, 2) == ["a", "c"]
    assert top_spenders(ORDERS, 10) == ["a", "c", "b"]

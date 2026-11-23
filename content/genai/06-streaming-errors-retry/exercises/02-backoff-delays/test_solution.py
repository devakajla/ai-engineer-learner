from solution import backoff_delays


def test_examples():
    assert backoff_delays(4) == [1, 2, 4, 8]
    assert backoff_delays(6, base=1, cap=10) == [1, 2, 4, 8, 10, 10]
    assert backoff_delays(3, base=0.5) == [0.5, 1.0, 2.0]
    assert backoff_delays(0) == []


def test_edges():
    assert backoff_delays(1) == [1]
    assert backoff_delays(3, base=2, cap=3) == [2, 3, 3], "every wait is capped"
    assert backoff_delays(8)[-1] == 30, "128 is capped to 30 by default"
    assert len(backoff_delays(5)) == 5

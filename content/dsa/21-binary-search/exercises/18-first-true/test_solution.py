from solution import first_true


def test_examples():
    assert first_true([False, False, True, True]) == 2
    assert first_true([False, False]) == 2


def test_edges():
    assert first_true([]) == 0
    assert first_true([True]) == 0
    assert first_true([False]) == 1
    assert first_true([True, True, True]) == 0


def test_all_splits():
    for n in range(0, 12):
        for k in range(0, n + 1):
            flags = [False] * k + [True] * (n - k)
            assert first_true(flags) == k, f"{flags}"

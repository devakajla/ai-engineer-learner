from solution import count_queens


def test_examples():
    assert count_queens(4) == 2
    assert count_queens(1) == 1


def test_known_values():
    known = {1: 1, 2: 0, 3: 0, 4: 2, 5: 10, 6: 4, 7: 40, 8: 92}
    for n, want in known.items():
        assert count_queens(n) == want, f"n = {n}"

from solution import allowed_complexity


def test_examples():
    assert allowed_complexity(1000) == "O(n^2)"
    assert allowed_complexity(10**5) == "O(n log n)"


def test_boundaries():
    cases = [
        (1, "O(n!)"), (10, "O(n!)"), (11, "O(2^n)"), (20, "O(2^n)"),
        (21, "O(n^3)"), (500, "O(n^3)"), (501, "O(n^2)"), (5000, "O(n^2)"),
        (5001, "O(n log n)"), (10**6, "O(n log n)"), (10**6 + 1, "O(n)"),
        (10**8, "O(n)"), (10**8 + 1, "O(log n)"),
    ]
    for n, want in cases:
        assert allowed_complexity(n) == want, f"n={n}: expected {want}, got {allowed_complexity(n)}"
